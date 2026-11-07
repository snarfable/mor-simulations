#!/usr/bin/env python3
"""
Extract Chain R (Mu-Opioid Receptor) and Chain D (DAMGO peptide agonist) from 6DDF.pdb.
Chain D provides the experimental crystallographic reference for the orthosteric binding pocket.
"""

import sys

def extract_chains(pdb_file, receptor_file, pocket_ref_file):
    with open(pdb_file, 'r') as fin, \
         open(receptor_file, 'w') as fout_rec, \
         open(pocket_ref_file, 'w') as fout_damgo:
        
        for line in fin:
            if line.startswith(('ATOM', 'HETATM')):
                chain_id = line[21]
                if chain_id == 'R':
                    fout_rec.write(line)
                elif chain_id == 'D':
                    fout_damgo.write(line)
            elif line.startswith('TER'):
                chain_id = line[21] if len(line) > 21 else ''
                if chain_id == 'R':
                    fout_rec.write(line)
                elif chain_id == 'D':
                    fout_damgo.write(line)

        fout_rec.write('END\n')
        fout_damgo.write('END\n')

    print(f"Extracted MOR receptor (Chain R) to {receptor_file}")
    print(f"Extracted pocket reference DAMGO (Chain D) to {pocket_ref_file}")

if __name__ == '__main__':
    pdb_file = sys.argv[1] if len(sys.argv) > 1 else '6DDF.pdb'
    receptor_file = sys.argv[2] if len(sys.argv) > 2 else 'receptor.pdb'
    pocket_ref_file = sys.argv[3] if len(sys.argv) > 3 else 'damgo.pdb'
    extract_chains(pdb_file, receptor_file, pocket_ref_file)
