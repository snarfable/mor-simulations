#!/usr/bin/env bash
set -e

echo "=========================================================================="
echo " MOR Simulation Setup: Amphipol Augmentation & Ligand Binding Pipeline"
echo "=========================================================================="

echo "=== 1. Setting up Python virtual environment and dependencies ==="
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --quiet rdkit acpype pdbfixer openmm numpy

echo "=== 2. Downloading Mu-Opioid Receptor Structure (PDB: 6DDF) ==="
if [ ! -f "6DDF.pdb" ]; then
    wget -q -c https://files.rcsb.org/download/6DDF.pdb -O 6DDF.pdb
fi

echo "=== 3. Extracting Chain R (MOR) and Chain D (DAMGO pocket reference) ==="
python3 extract_chain.py

echo "=== 4. Rebuilding missing heavy atoms using PDBFixer ==="
pdbfixer receptor.pdb --output=receptor_fixed.pdb --add-atoms=heavy

echo "=== 5. Processing receptor topology with GROMACS pdb2gmx ==="
gmx pdb2gmx -f receptor_fixed.pdb -o conf.gro -p topol.top -i posre.itp -water tip3p -ff amber99sb-ildn -ignh

echo "=== 6. Generating and docking 12-bromo-7-hydroxymitragynine into orthosteric pocket ==="
python3 dock_ligand.py

echo "=== 7. Parameterizing docked ligand using ACPYPE (GAFF2) ==="
acpype -i ligand_docked.pdb -c gas -n 0 -a gaff2 -b ligand_docked

echo "=== 8. Synthesizing and parameterizing Amphipol A8-35 ==="
python3 build_amphipol.py

echo "=== 9. Assembling MOR-Amphipol-Ligand complex and integrating topologies ==="
python3 assemble_system.py

echo "=== 10. Generating GROMACS index groups for pulling and umbrella sampling ==="
python3 make_index.py

echo "=== 11. Initializing umbrella sampling window templates ==="
python3 setup_umbrella_windows.py

echo "=== 12. Compiling initial simulation binary with gmx grompp ==="
gmx grompp -f em.mdp -c complex_amphipol.gro -p topol.top -o run.tpr -maxwarn 1

echo "=========================================================================="
echo " Setup completed successfully! System is ready for solvation & sampling."
echo "=========================================================================="
