#!/usr/bin/env python3
"""
build_amphipol.py:
Constructs representative Amphipol A8-35 polymer chains matching the experimental
chemical composition (~35% acrylic acid, ~25% octylamide, ~40% isopropylamide),
optimizes their 3D conformations, and parameterizes them using ACPYPE and GAFF2.
"""

import os
import sys
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

AMPHIPOL_SMILES = (
    "CCC(C(=O)NC(C)C)CC(C(=O)O)CC(C(=O)NCCCCCCCC)"
    "CC(C(=O)NC(C)C)CC(C(=O)O)CC(C(=O)NCCCCCCCC)"
    "CC(C(=O)NC(C)C)CC(C(=O)O)"
)

def build_amphipol(pdb_output='apol_single.pdb'):
    print("Generating 3D Amphipol A8-35 chain conformer...")
    mol = Chem.MolFromSmiles(AMPHIPOL_SMILES)
    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.useRandomCoords = True
    params.maxIterations = 500
    res = AllChem.EmbedMolecule(mol, params)
    if res != 0:
        AllChem.EmbedMolecule(mol)
    AllChem.UFFOptimizeMolecule(mol, maxIters=1000)

    # Center coordinates at origin
    conf = mol.GetConformer()
    pos = conf.GetPositions()
    pos -= np.mean(pos, axis=0)
    for i in range(mol.GetNumAtoms()):
        conf.SetAtomPosition(i, pos[i])

    Chem.MolToPDBFile(mol, pdb_output)
    print(f"Amphipol A8-35 chain saved to {pdb_output} ({mol.GetNumAtoms()} atoms)")

    # Run ACPYPE parameterization
    acpype_bin = sys.executable.replace('python3', 'acpype')
    if not os.path.exists(acpype_bin):
        acpype_bin = 'acpype'

    cmd = [acpype_bin, '-i', pdb_output, '-c', 'gas', '-n', '0', '-a', 'gaff2', '-b', 'apol']
    print(f"Running ACPYPE: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("Amphipol A8-35 parameterized successfully via ACPYPE!")

if __name__ == '__main__':
    import numpy as np
    pdb_out = sys.argv[1] if len(sys.argv) > 1 else 'apol_single.pdb'
    build_amphipol(pdb_out)
