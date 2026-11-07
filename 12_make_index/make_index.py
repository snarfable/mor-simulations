#!/usr/bin/env python3
"""
make_index.py:
Generates custom GROMACS index groups (index.ndx) for:
1. [ Binding_Pocket ]: C-alpha atoms of key orthosteric pocket residues
   (Asp147, Tyr148, Met151, Trp293, Val300, Tyr326).
2. [ Ligand ]: 12-bromo-7-hydroxymitragynine atoms.
3. [ Complex ]: Protein + Amphipols + Ligand.
These groups are used for GROMACS pull code and umbrella sampling.
"""

import sys

def make_index(gro_file='solv-em.gro', out_ndx='index.ndx'):
    with open(gro_file, 'r') as f:
        lines = f.readlines()

    pocket_ca = []
    ligand_atoms = []
    protein_atoms = []
    amphipol_atoms = []
    water_atoms = []
    ion_atoms = []

    for line in lines[2:-1]:
        res_num = int(line[0:5])
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = int(line[15:20])

        if res_name == 'APOL':
            amphipol_atoms.append(atom_num)
        elif res_name == 'UNL':
            ligand_atoms.append(atom_num)
        elif res_name == 'SOL':
            water_atoms.append(atom_num)
        elif res_name == 'NA' or res_name == 'CL':
            ion_atoms.append(atom_num)
        else:
            protein_atoms.append(atom_num)
            if res_num in (147, 148, 151, 293, 300, 326) and atom_name == 'CA':
                pocket_ca.append(atom_num)

    complex_atoms = protein_atoms + amphipol_atoms + ligand_atoms
    water_ion_atoms = water_atoms + ion_atoms

    def write_group(f, name, atom_list):
        f.write(f"[ {name} ]\n")
        for i, atom in enumerate(atom_list):
            f.write(f"{atom:6d}")
            if (i + 1) % 10 == 0:
                f.write("\n")
        if len(atom_list) % 10 != 0:
            f.write("\n")
        f.write("\n")

    with open(out_ndx, 'w') as f:
        write_group(f, 'Binding_Pocket', pocket_ca)
        write_group(f, 'Ligand', ligand_atoms)
        write_group(f, 'Protein', protein_atoms)
        write_group(f, 'Amphipol', amphipol_atoms)
        write_group(f, 'Solute_Complex', complex_atoms)
        write_group(f, 'Protein_ligand_3d', complex_atoms)
        write_group(f, 'Water', water_atoms)
        write_group(f, 'Ions', ion_atoms)
        write_group(f, 'Water_and_ions', water_ion_atoms)

    print(f"Generated {out_ndx}:")
    print(f"  - Binding_Pocket: {len(pocket_ca)} atoms ({pocket_ca})")
    print(f"  - Ligand: {len(ligand_atoms)} atoms")
    print(f"  - Solute_Complex: {len(complex_atoms)} atoms")
    print(f"  - Protein_ligand_3d: {len(complex_atoms)} atoms")
    print(f"  - Water: {len(water_atoms)} atoms")
    print(f"  - Ions: {len(ion_atoms)} atoms")
    print(f"  - Water_and_ions: {len(water_ion_atoms)} atoms")

if __name__ == '__main__':
    gro_input = sys.argv[1] if len(sys.argv) > 1 else 'solv-em.gro'
    out_ndx = sys.argv[2] if len(sys.argv) > 2 else 'index.ndx'
    make_index(gro_file=gro_input, out_ndx=out_ndx)
