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
pip install --quiet rdkit acpype pdbfixer openmm numpy mpi4py pytest

echo "=== 2. Configuring and executing modular CMake simulation pipeline ==="
cmake -B build
cmake --build build --target mor_pipeline

echo "=========================================================================="
echo " Setup completed successfully! System is ready for solvation & sampling."
echo "=========================================================================="

