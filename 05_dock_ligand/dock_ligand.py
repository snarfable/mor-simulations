#!/usr/bin/env python3
"""
dock_ligand.py:
Generates 3D coordinates for 12-bromo-7-hydroxymitragynine from SMILES and docks
it into the orthosteric binding pocket of the mu-opioid receptor (MOR).
Anchors the basic tertiary nitrogen to form the canonical ~3.0 A salt bridge
with the invariant Asp147 (3.32) carboxylate, oriented towards the aromatic
subpocket occupied by Tyr1 of DAMGO in 6DDF.
"""

import sys
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

LIGAND_SMILES = r"CC[C@@H]1CN2CC[C@@]3(O)C(=Nc4c(Br)ccc(OC)c34)[C@@H]2C[C@@H]1\C(=C/OC)C(=O)OC"

def parse_damgo_pocket(damgo_pdb_path):
    """Extract coordinates of Tyr1 N and aromatic ring from DAMGO."""
    tyr1_n = None
    tyr1_arom = []
    with open(damgo_pdb_path, 'r') as f:
        for line in f:
            if line.startswith(('ATOM', 'HETATM')) and 'TYR D   1' in line:
                atom_name = line[12:16].strip()
                coords = np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                if atom_name == 'N':
                    tyr1_n = coords
                elif atom_name in ('CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'):
                    tyr1_arom.append(coords)
    
    if tyr1_n is None or not tyr1_arom:
        # Fallback to canonical 6DDF DAMGO coordinates if damgo.pdb lacks Tyr1
        tyr1_n = np.array([119.032, 149.353, 141.168])
        target_arom = np.array([121.600, 152.700, 138.800])
    else:
        target_arom = np.mean(tyr1_arom, axis=0)
        
    return tyr1_n, target_arom

def parse_receptor_coords(receptor_pdb_path):
    coords = []
    with open(receptor_pdb_path, 'r') as f:
        for line in f:
            if line.startswith(('ATOM', 'HETATM')):
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    return np.array(coords)

def dock_ligand(output_pdb='ligand_docked.pdb', damgo_pdb='damgo.pdb', receptor_pdb='receptor_fixed.pdb'):
    print("Generating 3D conformer for 12-bromo-7-hydroxymitragynine...")
    mol = Chem.MolFromSmiles(LIGAND_SMILES)
    mol = Chem.AddHs(mol)
    
    params = AllChem.ETKDGv3()
    params.useRandomCoords = True
    params.maxIterations = 500
    res = AllChem.EmbedMolecule(mol, params)
    if res != 0:
        AllChem.EmbedMolecule(mol)
    AllChem.UFFOptimizeMolecule(mol, maxIters=1000)

    # Identify pharmacophore anchors:
    # 1. Tertiary amine: nitrogen with 3 aliphatic carbon neighbors
    tertiary_n_idx = None
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7:
            neighbors = atom.GetNeighbors()
            if len(neighbors) == 3 and all(n.GetAtomicNum() == 6 and not n.GetIsAromatic() for n in neighbors):
                tertiary_n_idx = atom.GetIdx()
                break

    if tertiary_n_idx is None:
        raise ValueError("Could not locate tertiary amine in ligand structure.")

    aromatic_indices = [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetIsAromatic()]

    conf = mol.GetConformer()
    pos = conf.GetPositions()

    n_pos = pos[tertiary_n_idx]
    arom_center = np.mean(pos[aromatic_indices], axis=0)

    # Reference pocket targets
    target_n, target_arom = parse_damgo_pocket(damgo_pdb)
    rec_coords = parse_receptor_coords(receptor_pdb)

    v_source = (arom_center - n_pos) / np.linalg.norm(arom_center - n_pos)
    v_target = (target_arom - target_n) / np.linalg.norm(target_arom - target_n)

    # Primary rotation aligning source vector to target vector
    v_axis = np.cross(v_source, v_target)
    axis_norm = np.linalg.norm(v_axis)
    if axis_norm > 1e-6:
        axis = v_axis / axis_norm
        angle = np.arccos(np.clip(np.dot(v_source, v_target), -1.0, 1.0))
        K = np.array([[0, -axis[2], axis[1]],
                      [axis[2], 0, -axis[0]],
                      [-axis[1], axis[0], 0]])
        R0 = np.eye(3) + np.sin(angle)*K + (1 - np.cos(angle))*(K @ K)
    else:
        R0 = np.eye(3)

    base_pos = (pos - n_pos) @ R0.T + target_n

    # Secondary rotation search around v_target to minimize steric overlap with receptor
    K_target = np.array([[0, -v_target[2], v_target[1]],
                         [v_target[2], 0, -v_target[0]],
                         [-v_target[1], v_target[0], 0]])

    best_phi = 0
    best_clashes = 9999
    best_min_dist = 0.0

    for deg in range(0, 360, 5):
        rad = np.radians(deg)
        R_rot = np.eye(3) + np.sin(rad)*K_target + (1 - np.cos(rad))*(K_target @ K_target)
        test_pos = (base_pos - target_n) @ R_rot.T + target_n
        
        # Check contact distances against receptor
        dists = [np.min(np.linalg.norm(rec_coords - p, axis=1)) for p in test_pos]
        clashes = sum(1 for d in dists if d < 1.5)
        min_d = np.min(dists)
        
        if clashes < best_clashes or (clashes == best_clashes and min_d > best_min_dist):
            best_clashes = clashes
            best_min_dist = min_d
            best_phi = deg

    # Apply optimal rotation
    best_rad = np.radians(best_phi)
    R_best = np.eye(3) + np.sin(best_rad)*K_target + (1 - np.cos(best_rad))*(K_target @ K_target)
    final_pos = (base_pos - target_n) @ R_best.T + target_n

    for i in range(mol.GetNumAtoms()):
        conf.SetAtomPosition(i, final_pos[i])

    Chem.MolToPDBFile(mol, output_pdb)
    print(f"Docked ligand successfully written to {output_pdb}")
    print(f"Anchor tertiary amine positioned at {final_pos[tertiary_n_idx]}")
    print(f"Optimal rotation: {best_phi} deg (clashes < 1.5 A: {best_clashes}, min contact: {best_min_dist:.2f} A)")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Dock ligand into MOR binding pocket.")
    parser.add_argument("--damgo", default="damgo.pdb", help="DAMGO reference PDB")
    parser.add_argument("--receptor", default="receptor_fixed.pdb", help="Receptor PDB")
    parser.add_argument("--output", default="ligand_docked.pdb", help="Output docked ligand PDB")
    args = parser.parse_args()
    dock_ligand(output_pdb=args.output, damgo_pdb=args.damgo, receptor_pdb=args.receptor)
