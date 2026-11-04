#!/usr/bin/env python3
"""
assemble_system.py:
Assembles the complete simulation system:
1. Active MOR receptor (conf.gro)
2. Docked 12-bromo-7-hydroxymitragynine (ligand_docked_GMX.gro)
3. Amphipol A8-35 annular belt (6 chains from apol_GMX.gro) wrapping the TM domain
4. Deduplicates GAFF2 atomtypes into extra_atomtypes.itp
5. Modularizes ligand.itp and apol.itp
6. Updates topol.top with correct topology inclusions and molecular counts
"""

import os
import sys
import numpy as np

def parse_gro(gro_file):
    with open(gro_file, 'r') as f:
        lines = f.readlines()
    title = lines[0].strip()
    num_atoms = int(lines[1].strip())
    atom_lines = lines[2:2 + num_atoms]
    box_line = lines[2 + num_atoms].strip()
    return title, num_atoms, atom_lines, box_line

def extract_coords(atom_lines):
    coords = []
    for line in atom_lines:
        coords.append([float(line[20:28]), float(line[28:36]), float(line[36:44])])
    return np.array(coords)

def format_gro_line(res_num, res_name, atom_name, atom_num, x, y, z):
    return f"{res_num:5d}{res_name:<5s}{atom_name:>5s}{atom_num:5d}{x:8.3f}{y:8.3f}{z:8.3f}\n"

def assemble_system(
    rec_gro='conf.gro',
    lig_gro='ligand_docked.acpype/ligand_docked_GMX.gro',
    apol_gro='apol.acpype/apol_GMX.gro',
    out_gro='complex_amphipol.gro',
    top_file='topol.top'
):
    print("Reading receptor, docked ligand, and amphipol coordinates...")
    _, rec_natoms, rec_lines, box = parse_gro(rec_gro)
    _, lig_natoms, lig_lines, _ = parse_gro(lig_gro)
    _, apol_natoms, apol_lines, _ = parse_gro(apol_gro)

    rec_coords = extract_coords(rec_lines)
    lig_coords = extract_coords(lig_lines)
    apol_base_coords = extract_coords(apol_lines)

    # 1. Determine transmembrane region center of mass from receptor coordinates
    # In conf.gro, MOR TM region is between Z = 11.8 nm and 13.8 nm
    tm_mask = (rec_coords[:, 2] >= 11.8) & (rec_coords[:, 2] <= 13.8)
    if np.any(tm_mask):
        tm_com = np.mean(rec_coords[tm_mask], axis=0)
    else:
        tm_com = np.mean(rec_coords, axis=0)

    print(f"Transmembrane center of mass (nm): X={tm_com[0]:.2f}, Y={tm_com[1]:.2f}, Z={tm_com[2]:.2f}")

    # 2. Place 6 Amphipol A8-35 chains in an annular ring around TM center of mass
    num_apol_chains = 6
    radius_belt = 2.65  # nm radius from TM bundle center of mass
    z_stagger = 0.30    # nm alternating Z offset

    all_atom_lines = []
    current_atom_num = 1

    # Add receptor atoms
    for line in rec_lines:
        res_num = int(line[0:5])
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        x = float(line[20:28])
        y = float(line[28:36])
        z = float(line[36:44])
        all_atom_lines.append(format_gro_line(res_num, res_name, atom_name, current_atom_num % 100000, x, y, z))
        current_atom_num += 1

    last_res_num = int(rec_lines[-1][0:5])

    # Add docked ligand atoms
    last_res_num += 1
    lig_res_name = "UNL"
    for i, line in enumerate(lig_lines):
        atom_name = line[10:15].strip()
        x, y, z = lig_coords[i]
        all_atom_lines.append(format_gro_line(last_res_num, lig_res_name, atom_name, current_atom_num % 100000, x, y, z))
        current_atom_num += 1

    # Add 6 Amphipol chains
    for k in range(num_apol_chains):
        last_res_num += 1
        theta = 2.0 * np.pi * k / num_apol_chains
        
        # Stagger vertical positions to cover top and bottom of hydrophobic belt
        z_offset = z_stagger if (k % 2 == 0) else -z_stagger

        center_k = np.array([
            tm_com[0] + radius_belt * np.cos(theta),
            tm_com[1] + radius_belt * np.sin(theta),
            tm_com[2] + z_offset
        ])

        # Rotation matrix around Z axis to face hydrophobic grafts inward
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        R_z = np.array([
            [cos_t, -sin_t, 0.0],
            [sin_t,  cos_t, 0.0],
            [0.0,    0.0,   1.0]
        ])

        # Transform single chain coordinates
        transformed_coords = apol_base_coords @ R_z.T + center_k

        for i, line in enumerate(apol_lines):
            atom_name = line[10:15].strip()
            x, y, z = transformed_coords[i]
            all_atom_lines.append(format_gro_line(last_res_num, "APOL", atom_name, current_atom_num % 100000, x, y, z))
            current_atom_num += 1

    total_atoms = len(all_atom_lines)

    # Write merged GRO
    with open(out_gro, 'w') as fo:
        fo.write("MOR in Amphipol A8-35 Belt with Docked 12-bromo-7-hydroxymitragynine\n")
        fo.write(f"{total_atoms}\n")
        fo.writelines(all_atom_lines)
        fo.write(f"{box}\n")

    print(f"Generated {out_gro} with {total_atoms} atoms (Receptor: {rec_natoms}, Ligand: {lig_natoms}, 6 Amphipols: {num_apol_chains * apol_natoms}).")

    # 3. Modularize topologies and deduplicate atomtypes
    print("Modularizing topologies and deduplicating GAFF2 atomtypes...")
    
    def parse_itp(itp_file):
        with open(itp_file) as f:
            lines = f.readlines()
        at_dict = {}
        mol_lines = []
        in_at = False
        in_mol = False
        for line in lines:
            s = line.strip()
            if s.startswith('[ atomtypes ]'):
                in_at = True
                in_mol = False
                continue
            elif s.startswith('[ moleculetype ]'):
                in_at = False
                in_mol = True
            elif s.startswith('[') and in_at:
                in_at = False

            if in_at:
                if s and not s.startswith(';'):
                    parts = s.split()
                    if len(parts) >= 6:
                        name = parts[0]
                        at_dict[name] = line
            elif in_mol:
                mol_lines.append(line)
        return at_dict, mol_lines

    lig_at, lig_mol = parse_itp('ligand_docked.acpype/ligand_docked_GMX.itp')
    apol_at, apol_mol = parse_itp('apol.acpype/apol_GMX.itp')

    # Deduplicate atomtypes
    merged_at = dict(lig_at)
    for name, line in apol_at.items():
        if name not in merged_at:
            merged_at[name] = line

    with open('extra_atomtypes.itp', 'w') as f:
        f.write("; Merged and deduplicated GAFF2 atomtypes for Ligand and Amphipols\n")
        f.write("[ atomtypes ]\n")
        for line in merged_at.values():
            f.write(line)

    with open('ligand.itp', 'w') as f:
        f.write("; Ligand moleculetype and parameters\n[ moleculetype ]\n")
        f.writelines(lig_mol)

    with open('apol.itp', 'w') as f:
        f.write("; Amphipol A8-35 moleculetype and parameters\n[ moleculetype ]\n")
        f.writelines(apol_mol)

    # 4. Update topol.top
    with open(top_file, 'r') as f:
        top_content = f.read()

    # Clean any previous custom includes
    for old_inc in ['#include "ligand_atomtypes.itp"\n',
                    '#include "extra_atomtypes.itp"\n',
                    '#include "ligand.itp"\n',
                    '#include "apol.itp"\n',
                    '#include "ligand_3d.acpype/ligand_3d_GMX.itp"\n']:
        top_content = top_content.replace(old_inc, '')

    ff_include = '#include "amber99sb-ildn.ff/forcefield.itp"'
    new_ff_include = f'{ff_include}\n#include "extra_atomtypes.itp"'
    top_content = top_content.replace(ff_include, new_ff_include)

    # Insert ligand.itp and apol.itp before [ system ]
    sys_pos = top_content.find('[ system ]')
    if sys_pos != -1:
        insert_text = '#include "ligand.itp"\n#include "apol.itp"\n\n'
        top_content = top_content[:sys_pos] + insert_text + top_content[sys_pos:]

    # Clean old molecule entries at bottom
    mol_pos = top_content.find('[ molecules ]')
    if mol_pos != -1:
        header = top_content[:mol_pos]
        mol_section = top_content[mol_pos:]
        mol_lines = [l for l in mol_section.splitlines() if not (
            l.strip().startswith('ligand_3d') or
            l.strip().startswith('ligand_docked') or
            l.strip().startswith('apol')
        )]
        mol_lines.append(f"{'ligand_docked':<17s} 1")
        mol_lines.append(f"{'apol':<17s} {num_apol_chains}")
        top_content = header + '\n'.join(mol_lines) + '\n'

    with open(top_file, 'w') as f:
        f.write(top_content)

    print("Master topology topol.top updated successfully.")

if __name__ == '__main__':
    assemble_system()
