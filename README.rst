=====================================================================================
Umbrella Sampling of 12-Bromo-7-Hydroxymitragynine Binding to the Mu-Opioid Receptor
=====================================================================================

.. image:: https://img.shields.io/badge/GROMACS-2023+-blue.svg
   :target: https://www.gromacs.org
.. image:: https://img.shields.io/badge/PLUMED-2.8+-orange.svg
   :target: https://www.plumed.org
.. image:: https://img.shields.io/badge/ForceField-Amber99SB--ILDN%20%2F%20GAFF2-green.svg
   :target: https://ambermd.org
.. image:: https://img.shields.io/badge/Membrane%20Mimetic-Amphipol%20A8--35-teal.svg
   :target: https://www.anatrace.com
.. image:: https://img.shields.io/badge/Target-Mu--Opioid%20Receptor%20(6DDF)-red.svg
   :target: https://www.rcsb.org/structure/6DDF

Overview
========

This repository establishes a complete, automated molecular dynamics (MD) and enhanced
sampling pipeline to calculate the binding free energy profile and mechanism of
**12-bromo-7-hydroxymitragynine** interacting with the **human μ-opioid receptor
(μOR / MOR)**.

The μ-opioid receptor is a prototypical class A G protein-coupled receptor (GPCR)
responsible for mediating clinical opioid analgesia as well as dose-limiting adverse
liabilities (respiratory depression, constipation, physical dependence, and tolerance).
**12-bromo-7-hydroxymitragynine** is a halogenated derivative of 7-hydroxymitragynine,
the active oxidized alkaloidal metabolite of *Mitragyna speciosa* (kratom). Pharmacological
assays demonstrate that this compound functions as an atypical agonist or G-protein-biased
ligand with markedly reduced β-arrestin-2 recruitment, making it a prominent lead for
next-generation analgesics.

To determine the unbinding/binding thermodynamics and free energy landscape
(:math:`\Delta G_{\text{bind}}`), this repository implements:

1. **Membrane Mimetic Augmentation with Amphipol A8-35**:
   Because transmembrane GPCRs undergo rapid tertiary denaturation and non-physiological
   collapse when stripped of membrane support in aqueous solvent, the 7-transmembrane
   (7TM) helical bundle is augmented with an annular belt of **Amphipol A8-35** polymers.
   This stabilizes the hydrophobic core while maintaining full solvent accessibility for
   extracellular ligand entry and intracellular conformational dynamics.

2. **Targeted Orthosteric Pocket Docking**:
   The ligand is structurally aligned into the orthosteric binding pocket using the
   crystallographic position of the bound peptide agonist DAMGO from PDB 6DDF. The
   ligand's basic tertiary nitrogen is anchored at a canonical :math:`\sim 3.0\text{ \AA}`
   salt bridge distance from the invariant **Asp147**\ :sup:`3.32` carboxylate, with the
   bromomethoxyindole core positioned in the aromatic subpocket near **Trp293**\ :sup:`6.48`.

3. **Umbrella Sampling along the Binding Axis**:
   Steered molecular dynamics (SMD) gently pulls the ligand from the bound pocket
   (:math:`d \approx 0.40\text{ nm}`) out through the extracellular vestibule into bulk
   solvent (:math:`d \approx 2.50\text{ nm}`). 22 harmonic umbrella sampling windows
   are sampled and evaluated via the Weighted Histogram Analysis Method (WHAM) to
   recover the Potential of Mean Force (PMF).

Membrane Mimetic: Amphipol A8-35 Augmentation
=============================================

Amphipols are amphipathic polymers designed to substitute for detergents or complex lipid
bilayers when handling transmembrane proteins. Specifically, **Amphipol A8-35** is a
random terpolymer derived from polyacrylic acid with an approximate molecular stoichiometry
of:

- **~35 mol% Free carboxylates** (:math:`-\text{CH}_2-\text{CH}(\text{COO}^-)-`):
  hydrophilic, ensuring high aqueous solubility.
- **~25 mol% Octylamide grafts** (:math:`-\text{CH}_2-\text{CH}(\text{CONH}-(\text{CH}_2)_7\text{CH}_3)-`):
  hydrophobic, anchoring into the nonpolar transmembrane surface.
- **~40 mol% Isopropylamide grafts** (:math:`-\text{CH}_2-\text{CH}(\text{CONH}-\text{CH}(\text{CH}_3)_2)-`):
  branched hydrophobic groups providing lateral packing.

Rationale for Amphipol Augmentation:
------------------------------------

- **Preservation of the 7TM Architecture**: The hydrophobic octyl and isopropyl chains
  wrap around the nonpolar transmembrane helices (TM1 through TM7), shielding exposed
  aliphatic residues from aqueous solvent without dissociating upon dilution.
- **Unrestricted Loop and Vestibule Dynamics**: Unlike planar periodic bilayers that
  constrain simulation box dimensions and solvent volumes, the amphipol belt leaves both
  the extracellular loops (ECL1–ECL3, governing the ligand binding pathway) and
  intracellular loops (ICL1–ICL3) unhindered.
- **Accelerated Convergence & Reduced Atom Counts**: Amphipol-solubilized GPCR complexes
  require significantly fewer atoms than large phospholipid bilayers (e.g., POPC/cholesterol)
  and avoid long multi-nanosecond bilayer area-per-lipid equilibration times.

The script ``07_build_amphipol/build_amphipol.py`` generates representative 3D Amphipol A8-35
chains and parameterizes them with GAFF2/AMBER via ACPYPE. The script
``08_assemble_system/assemble_system.py`` detects the transmembrane region of MOR
(:math:`Z \in [11.8, 13.8]\text{ nm}`, radius :math:`R \approx 2.65\text{ nm}`) and
positions 6 amphipol chains concentrically around the receptor, with hydrophobic side chains
facing inward and carboxylates facing outward.

Modular CMake Build System & Pipeline
=====================================

The end-to-end preparation, minimization, solvation, and equilibration workflow is organized
as a modular, dependency-driven **CMake build system**. Each discrete setup and simulation
stage is isolated in its own numbered subdirectory with a dedicated ``CMakeLists.txt`` and
explicit input/output file targets.

Furthermore, **GROMACS** is fetched and built in-source via CMake's ``FetchContent`` module
directly from `https://github.com/gromacs/gromacs.git` with custom configuration options
(threaded MPI, OpenMP, GMXAPI, internal FFTW, and Python bindings).

.. code-block:: text

   +---------------------------------------------------------------------------------------+
   |                             MODULAR CMAKE PIPELINE                                    |
   +---------------------------------------------------------------------------------------+
   |                                                                                       |
   |   [FetchContent] GROMACS in-source build (target: gmx)                                |
   |            |                                                                          |
   |   [01_download_pdb]     ----> Downloads/copies active MOR complex (PDB: 6DDF)         |
   |            |                                                                          |
   |   [02_extract_chains]   ----> Isolates Chain R (MOR) & Chain D (DAMGO pocket)         |
   |            |                                                                          |
   |   [03_rebuild_atoms]    ----> PDBFixer repairs missing heavy atoms and loops          |
   |            |                                                                          |
   |   [04_receptor_topology]----> gmx pdb2gmx builds AMBER99SB-ILDN receptor topology     |
   |            |                                                                          |
   |   [05_dock_ligand]      ----> RDKit conformer generation & targeted docking to Asp147|
   |            |                                                                          |
   |   [06_ligand_params]    ----> ACPYPE parameterizes docked ligand (GAFF2)              |
   |            |                                                                          |
   |   [07_build_amphipol]   ----> Synthesizes & parameterizes Amphipol A8-35 (GAFF2)      |
   |            |                                                                          |
   |   [08_assemble_system]  ----> Wraps 6 A8-35 chains around TM bundle & integrates .top|
   |            |                                                                          |
   |   [09_em_complex]       ----> In-vacuo steepest descent minimization (gmx grompp/run)|
   |            |                                                                          |
   |   [10_solvate]          ----> Dodecahedron box, explicit TIP3P water, 0.15 M NaCl    |
   |            |                                                                          |
   |   [11_em_solv]          ----> Solvated & neutralized system energy minimization       |
   |            |                                                                          |
   |   [12_make_index]       ----> Generates index groups for pulling & temperature coupling|
   |            |                                                                          |
   |   [13_nvt]              ----> NVT equilibration (100 ps, 310 K)                       |
   |            |                                                                          |
   |   [14_setup_umbrella]   ----> Prepares 22 harmonic umbrella sampling window templates |
   |            |                                                                          |
   |   [15_production]       ----> Copies production MDPs (NPT, Pulling, AWH) & PLUMED data|
   |                                                                                       |
   +---------------------------------------------------------------------------------------+

Pipeline Stages Detailed
------------------------

0. GROMACS In-Source Compilation (FetchContent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The top-level ``CMakeLists.txt`` declares and populates GROMACS from its official Git
repository. It builds the ``gmx`` executable target with the following parameters:

- ``-DGMX_PYTHON_PACKAGE=ON``: Builds the Python package for ``gmxapi``.
- ``-DGMXAPI=ON``: Enables GROMACS C++ API and workflow interface.
- ``-DGMXAPI_BUILD_DOCS=OFF``: Disables extra documentation generation for speed.
- ``-DGMX_BUILD_OWN_FFTW=ON``: Automatically builds internal FFTW with AVX2 SIMD acceleration.
- ``-DGMX_TMPI=ON``: Enables built-in thread-MPI for high-performance intra-node scaling.
- ``-DGMX_OPENMP=ON``: Enables OpenMP multithreading across CPU cores.
- Automated source patching via ``cmake/patch_gromacs.py`` ensures all subproject paths
  resolve correctly to ``${Gromacs_SOURCE_DIR}``.

1. Structure Acquisition (``01_download_pdb``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``01_download_pdb`` (Output: ``build/01_download_pdb/6DDF.pdb``)

Retrieves the 3.5 Å resolution cryo-EM structure of the active-state human μ-opioid
receptor bound to DAMGO and Gi protein (PDB ``6DDF``).

2. Receptor and Reference Pocket Extraction (``02_extract_chains``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``02_extract_chains`` (Outputs: ``receptor.pdb``, ``damgo.pdb``)

Executes ``extract_chain.py`` on ``6DDF.pdb`` to isolate:

- ``receptor.pdb``: Chain R (human μ-opioid receptor).
- ``damgo.pdb``: Chain D (DAMGO peptide agonist), providing the crystallographic
  reference coordinates of the orthosteric binding pocket.

3. Heavy Atom & Side-Chain Rebuilding (``03_rebuild_atoms``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``03_rebuild_atoms`` (Output: ``receptor_fixed.pdb``)

Invokes ``pdbfixer`` to detect and rebuild missing side-chain heavy atoms and unresolved
residues within the receptor transmembrane bundle.

4. Receptor Topology Generation (``04_receptor_topology``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``04_receptor_topology`` (Outputs: ``conf.gro``, ``topol.top``, ``posre.itp``)

Executes the in-source ``gmx pdb2gmx`` binary using the **Amber99SB-ILDN** force field and
the **TIP3P** water model. Detects the conserved Cys140–Cys217 disulfide bridge connecting
TM3 to ECL2.

5. Ligand Conformer Generation & Targeted Docking (``05_dock_ligand``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``05_dock_ligand`` (Output: ``ligand_docked.pdb``)

The script ``dock_ligand.py`` reads the isomeric SMILES of 12-bromo-7-hydroxymitragynine:

.. code-block:: text

   CC[C@@H]1CN2CC[C@@]3(O)C(=Nc4c(Br)ccc(OC)c34)[C@@H]2C[C@@H]1\C(=C/OC)C(=O)OC

It performs 3D distance geometry embedding (ETKDGv3), optimizes the conformer with UFF,
identifies the basic tertiary amine (N4), and performs a targeted spatial alignment:

- Anchors the tertiary amine to the position occupied by the Tyr1 amino group of DAMGO,
  forming a :math:`\sim 3.0\text{ \AA}` salt bridge with the carboxylate oxygens of
  **Asp147**\ :sup:`3.32`.
- Directs the bromomethoxyindole core towards the hydrophobic/aromatic subpocket
  occupied by Tyr1 of DAMGO and flanked by **Trp293**\ :sup:`6.48`.
- Scans rotational orientations around the anchoring axis to eliminate steric clashes
  with receptor residues, outputting ``ligand_docked.pdb``.

6. Ligand Parameterization (``06_ligand_params``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``06_ligand_params`` (Outputs: ``ligand_docked.acpype/ligand_docked_GMX.gro``, ``.itp``)

ACPYPE parameterizes the docked ligand using GAFF2 and Gasteiger partial atomic charges.

7. Amphipol A8-35 Synthesis & Parameterization (``07_build_amphipol``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``07_build_amphipol`` (Outputs: ``apol_single.pdb``, ``apol.acpype/apol_GMX.gro``, ``.itp``)

The script ``build_amphipol.py`` constructs the Amphipol A8-35 chain matching the
experimental 35:25:40 monomer stoichiometry, embeds and minimizes the 3D conformer,
and invokes ACPYPE to generate GAFF2 parameters.

8. Complex Assembly & Topology Integration (``08_assemble_system``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``08_assemble_system`` (Outputs: ``complex_amphipol.gro``, ``topol.top``, ``extra_atomtypes.itp``, ``ligand.itp``, ``apol.itp``)

The script ``assemble_system.py`` combines all components into ``complex_amphipol.gro``:

- Determines the receptor's transmembrane center of mass.
- Arranges 6 Amphipol A8-35 chains in an annular belt (:math:`R \approx 2.65\text{ nm}`)
  surrounding the 7TM bundle, with alternating :math:`\pm 0.3\text{ nm}` vertical staggering.
  Chains are rotated so that hydrophobic octyl and isopropyl chains face inward and
  hydrophilic carboxylates face outward into water.
- Integrates docked ligand coordinates.
- Modularizes topologies (``ligand.itp``, ``apol.itp``) and merges all GAFF2 atomtypes into
  a deduplicated ``extra_atomtypes.itp``.
- Updates ``topol.top`` with all inclusions and molecule counts.

9. In-Vacuo Energy Minimization (``09_em_complex``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``09_em_complex`` (Outputs: ``complex-em.tpr``, ``complex-em.gro``)

Runs ``gmx grompp`` and ``gmx mdrun`` to minimize the receptor-ligand-amphipol complex
in vacuo, relaxing initial steric contacts.

10. Explicit Water Solvation & Neutralization (``10_solvate``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``10_solvate`` (Outputs: ``box.gro``, ``solv.gro``, ``ions.tpr``, ``solv-ions.gro``)

- Generates a rhombic dodecahedron periodic box with 1.5 nm clearance (``gmx editconf``).
- Solvates the system with explicit TIP3P water using ``spc216.gro`` (``gmx solvate``).
- Neutralizes net charges and adds physiological 0.15 M NaCl counterions (``gmx genion``).

11. Solvated Energy Minimization (``11_em_solv``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``11_em_solv`` (Outputs: ``solv-em.tpr``, ``solv-em.gro``)

Executes steepest descent minimization on the solvated and neutralized system to relax
water molecules and counterions around the position-restrained solute complex.

12. Index Group Generation (``12_make_index``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``12_make_index`` (Output: ``index.ndx``)

The script ``make_index.py`` reads ``solv-em.gro`` and generates custom GROMACS index groups:

- ``[ Binding_Pocket ]``: C-alpha atoms of orthosteric pocket residues (Asp147, Tyr148,
  Met151, Trp293, Val300, Tyr326).
- ``[ Ligand ]``: All atoms of 12-bromo-7-hydroxymitragynine.
- ``[ Solute_Complex ]``: Receptor, amphipols, and ligand for temperature coupling.
- ``[ Water_and_ions ]``: Solvent and counterions.

13. NVT Equilibration (``13_nvt``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``13_nvt`` (Outputs: ``solv-nvt.tpr``, ``solv-nvt.gro``)

Performs 100 ps of NVT equilibration at 310 K using the V-rescale thermostat, relaxing
solvent and amphipol chains around the restrained receptor and ligand.

14. Umbrella Sampling Window Initialization (``14_setup_umbrella``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``14_setup_umbrella`` (Output: ``umbrella_setup.done``)

The script ``setup_umbrella_windows.py`` initializes 22 template directories across the
reaction coordinate range:

.. math::

   \xi_i \in [0.40, 0.50, 0.60, \dots, 2.40, 2.50]\text{ nm}

Each window folder receives a customized ``umbrella.mdp`` with the appropriate reference
distance ``pull-coord1-init = <xi_i>``.

15. Production Simulation Templates (``15_production``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Target: ``15_production`` (Output: ``production_templates.done``)

Stages simulation parameter templates (``npt.mdp``, ``pull.mdp``, ``awh.mdp``, ``md.mdp``)
and PLUMED collective variable definitions (``plumed.dat``, ``plumed_binding.dat``).

Simulation Protocols & CMake Targets
====================================

Each simulation phase corresponds to a discrete CMake target that automatically satisfies
all upstream dependencies before execution.

1. Complex In-Vacuo Minimization (``09_em_complex``)
----------------------------------------------------

Performs steepest descent minimization (:math:`F_{\text{max}} < 1000.0\text{ kJ/mol/nm}`)
on the dry receptor-ligand-amphipol assembly:

.. code-block:: bash

   cmake --build build --target 09_em_complex

2. Explicit Water Solvation & Neutralization (``10_solvate``)
-------------------------------------------------------------

The complex is embedded in a rhombic dodecahedron periodic box (1.5 nm buffer) and
solvated with explicit TIP3P water (using GROMACS's bundled ``spc216.gro`` solvent lattice)
and neutralized with 0.15 M NaCl:

.. code-block:: bash

   cmake --build build --target 10_solvate

3. Solvated Energy Minimization (``11_em_solv``)
------------------------------------------------

Relaxes water molecules and counterions while keeping the protein backbone and ligand
restrained:

.. code-block:: bash

   cmake --build build --target 11_em_solv

4. NVT Equilibration (``13_nvt``)
---------------------------------

Equilibrates solvent and amphipol chains around the position-restrained receptor and
ligand at 310 K for 100 ps:

.. code-block:: bash

   cmake --build build --target 13_nvt

5. NPT, Steered Pulling, and Umbrella Sampling
----------------------------------------------

Production parameter templates and collective variables are staged in ``build/15_production/``
and ``build/14_setup_umbrella/``:

- **NPT Equilibration** (``15_production/npt.mdp``): 100 ps, 1 bar isotropic pressure coupling.
- **Steered MD Pulling** (``15_production/pull.mdp``): Pulls ligand along reaction coordinate
  at :math:`v = 0.002\text{ nm/ps}` over 1000 ps.
- **Umbrella Windows** (``14_setup_umbrella/``): 22 sampling windows spaced :math:`0.10\text{ nm}`
  apart from :math:`\xi = 0.40\text{ nm}` to :math:`2.50\text{ nm}`.
- **WHAM Analysis**:
  .. code-block:: bash

     gmx wham -ix tpr_files.dat -if pullf_files.dat -o profile.xvg -hist histo.xvg -unit kJ

File Manifest
=============

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Directory / File
     - Description
   * - ``CMakeLists.txt``
     - Top-level CMake build script fetching GROMACS and orchestrating all 15 stages.
   * - ``cmake/patch_gromacs.py``
     - Source adapter script fixing internal GROMACS paths during FetchContent.
   * - ``setup_mor_simulation.sh``
     - Master automation script creating ``.venv`` and running the CMake pipeline.
   * - ``cleanup_mor_simulation.sh``
     - Cleans build artifacts and generated simulation files.
   * - ``01_download_pdb/``
     - Stage 1: Structure acquisition (downloads/copies ``6DDF.pdb``).
   * - ``02_extract_chains/``
     - Stage 2: Isolates receptor (Chain R) and DAMGO reference (Chain D) via ``extract_chain.py``.
   * - ``03_rebuild_atoms/``
     - Stage 3: Reconstructs missing heavy atoms using PDBFixer.
   * - ``04_receptor_topology/``
     - Stage 4: Generates AMBER99SB-ILDN receptor topology via ``gmx pdb2gmx``.
   * - ``05_dock_ligand/``
     - Stage 5: Targeted Asp147 docking of 12-bromo-7-OH-mitragynine via ``dock_ligand.py``.
   * - ``06_ligand_params/``
     - Stage 6: GAFF2 parameterization using ACPYPE.
   * - ``07_build_amphipol/``
     - Stage 7: Amphipol A8-35 polymer synthesis and parameterization via ``build_amphipol.py``.
   * - ``08_assemble_system/``
     - Stage 8: System assembly, belt placement, and topology merger via ``assemble_system.py``.
   * - ``09_em_complex/``
     - Stage 9: In-vacuo complex energy minimization (``em.mdp``).
   * - ``10_solvate/``
     - Stage 10: Box generation, explicit TIP3P solvation, and 0.15 M NaCl ionization.
   * - ``11_em_solv/``
     - Stage 11: Energy minimization of the solvated/ionized system (``em.mdp``).
   * - ``12_make_index/``
     - Stage 12: Index group generation via ``make_index.py`` and PyMOL helper ``load_ndx.py``.
   * - ``13_nvt/``
     - Stage 13: 100 ps NVT thermal equilibration at 310 K (``nvt.mdp``).
   * - ``14_setup_umbrella/``
     - Stage 14: Umbrella sampling window initialization via ``setup_umbrella_windows.py``.
   * - ``15_production/``
     - Stage 15: Parameter templates (``npt.mdp``, ``pull.mdp``, ``awh.mdp``, ``md.mdp``, PLUMED files).

Prerequisites & Requirements
============================

System Toolchains:
------------------

- **C & C++ Compilers**: GCC 11+ or Clang supporting C++17.
- **CMake**: Version 3.20 or higher (3.28+ recommended).
- **Git**: For FetchContent submodule and GROMACS repository retrieval.
- **OpenMP & MPI Libraries**: Recommended for multithreaded simulation and ``gmxapi`` compatibility.
- **wget / curl**: For downloading structural databases.

*Note: GROMACS is built automatically in-source by CMake from the official repository.*

Python Dependencies:
--------------------

Installed automatically into ``.venv`` by ``setup_mor_simulation.sh``:

- ``rdkit``: Conformer generation and pocket docking geometry.
- ``acpype``: Automated GAFF2 parameterization for ligands and polymers.
- ``pdbfixer`` & ``openmm``: Structural repair and missing loop/atom reconstruction.
- ``numpy``: Coordinate transformations and vector math.
- ``mpi4py``: Required for GROMACS ``gmxapi`` Python bindings.
- ``pytest``: Required for GROMACS Python package verification.

Quickstart
==========

Automated Run (Scripted)
------------------------

Run the master script to install dependencies, configure CMake, and execute the entire pipeline:

.. code-block:: bash

   chmod +x setup_mor_simulation.sh
   ./setup_mor_simulation.sh

Native CMake Build Workflow
---------------------------

Or manage and run the build steps directly with CMake:

.. code-block:: bash

   # 1. (Optional) Create virtual environment if desired:
   python3 -m venv .venv
   source .venv/bin/activate

   # 2. Configure project out-of-source:
   # (CMake automatically detects and installs any missing Python packages
   #  such as rdkit, mpi4py, pdbfixer, openmm, numpy, pybind11, pytest, acpype)
   cmake -B build

   # 3. Explicitly install or update Python packages anytime via target:
   cmake --build build --target python_dependencies

   # 4. Configure with GPU compute and custom mdrun offload flags:
   # (When GMX_GPU is enabled and GMX_MDRUN_GPU_FLAGS is omitted, it defaults to:
   #  "-nb gpu -pme gpu -pmefft gpu -bonded gpu -update gpu")
   cmake -B build -DGMX_GPU=CUDA -DGMX_MDRUN_GPU_FLAGS="-nb gpu -pme gpu -pmefft gpu -bonded gpu -update gpu"

   # 5. Build a specific stage (e.g., dock ligand, which builds all upstream prerequisites)
   cmake --build build --target 05_dock_ligand

   # 6. Or execute the entire pipeline
   cmake --build build --target mor_pipeline

Scientific References
=====================

- **Active-State Mu-Opioid Receptor Structure**:
  Koehl, A. et al. (2018). *Structure of the μ-opioid receptor-Gi protein complex*.
  Nature, 558(7711), 547–552. https://doi.org/10.1038/s41586-018-0219-7

- **Mitragyna Alkaloids and Halogenated Derivatives**:
  Váradi, A. et al. (2016). *Mitragynine/7-Hydroxymitragynine as Precursors for
  Functionalized Opioid Receptor Ligands*. Journal of Medicinal Chemistry, 59(18),
  8381–8397. https://doi.org/10.1021/acs.jmedchem.6b00748

- **Amphipols as Membrane Protein Mimetics**:
  Popot, J.-L. et al. (2011). *Amphipols from A to Z*. Annual Review of Biophysics,
  40, 379–408. https://doi.org/10.1146/annurev-biophys-042910-155219

- **Molecular Dynamics Simulations of Amphipol A8-35**:
  Perlmutter, J. D. et al. (2011). *All-Atom and Coarse-Grained Molecular Dynamics
  Simulations of a Membrane Protein Stabilizing Polymer*. Langmuir, 27(17),
  10523–10537. https://doi.org/10.1021/la201736k

- **GROMACS**:
  Abraham, M. J. et al. (2015). *GROMACS: High performance molecular simulations
  through multi-level parallelism from laptops to supercomputers*. SoftwareX, 1–2, 19–25.

- **PLUMED**:
  Tribello, G. A. et al. (2014). *PLUMED 2: New feathers for an old bird*. Computer
  Physics Communications, 185(2), 604–613.

- **ACPYPE**:
  Sousa da Silva, A. W., & Vranken, W. F. (2012). *ACPYPE - AnteChamber PYthon Parser
  interfacE*. BMC Research Notes, 5, 367.
