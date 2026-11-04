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

The script ``build_amphipol.py`` generates representative 3D Amphipol A8-35 chains and
parameterizes them with GAFF2/AMBER via ACPYPE. The script ``assemble_system.py``
detects the transmembrane region of MOR (:math:`Z \in [11.8, 13.8]\text{ nm}`, radius
:math:`R \approx 2.65\text{ nm}`) and positions 6 amphipol chains concentrically around
the receptor, with hydrophobic side chains facing inward and carboxylates facing outward.

Automated Pipeline (`setup_mor_simulation.sh`)
==============================================

The end-to-end preparation is coordinated by ``setup_mor_simulation.sh``:

.. code-block:: text

   +-------------------------------------------------------------------------------+
   |                             SETUP WORKFLOW                                    |
   +-------------------------------------------------------------------------------+
   |                                                                               |
   |   [1] Virtualenv Setup ----> Installs RDKit, ACPYPE, PDBFixer, OpenMM, NumPy  |
   |            |                                                                  |
   |   [2] PDB Download    ----> Downloads active MOR complex (PDB 6DDF)           |
   |            |                                                                  |
   |   [3] Chain Extraction----> Isolates Chain R (MOR) & Chain D (DAMGO pocket)   |
   |            |                                                                  |
   |   [4] Atom Rebuilding ----> PDBFixer repairs missing heavy atoms and loops    |
   |            |                                                                  |
   |   [5] Protein Topology----> GROMACS pdb2gmx builds AMBER99SB-ILDN topology   |
   |            |                                                                  |
   |   [6] Ligand Docking  ----> RDKit generates 3D conformer & docks into Asp147  |
   |            |                                                                  |
   |   [7] Parameterization----> ACPYPE generates GAFF2 ligand parameters          |
   |            |                                                                  |
   |   [8] Amphipol Synth  ----> build_amphipol.py synthesizes & parameterizes    |
   |            |                Amphipol A8-35 with GAFF2                         |
   |            |                                                                  |
   |   [9] Complex Assembly----> assemble_system.py wraps 6 A8-35 chains around    |
   |            |                TM bundle, deduplicates atomtypes, & updates .top |
   |            |                                                                  |
   |  [10] Index Generation----> make_index.py builds Binding_Pocket & Ligand ndx  |
   |            |                                                                  |
   |  [11] US Window Setup ----> setup_umbrella_windows.py creates 22 window dirs  |
   |            |                                                                  |
   |  [12] Grompp Compile  ----> Validates topology & outputs binary run.tpr       |
   |                                                                               |
   +-------------------------------------------------------------------------------+

Pipeline Stages Detailed
------------------------

1. Python Virtual Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initializes a local Python virtual environment (``.venv``) and installs dependencies:

- ``rdkit``: Cheminformatics, conformer generation, and geometry optimization.
- ``acpype``: Automated GAFF2 parameterization for GROMACS.
- ``pdbfixer`` & ``openmm``: Structural repair and missing loop/atom reconstruction.
- ``numpy``: Vector algebra for coordinate transformations and frame extraction.

2. Structure Acquisition (PDB: 6DDF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Downloads the 3.5 Å resolution cryo-EM structure of the active-state human μ-opioid
receptor bound to the peptide agonist DAMGO and heterotrimeric Gi protein (PDB ``6DDF``).

3. Receptor and Reference Pocket Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``extract_chain.py`` isolates:

- ``receptor.pdb``: Chain R (human μ-opioid receptor).
- ``damgo.pdb``: Chain D (DAMGO peptide agonist), providing the crystallographic
  reference coordinates of the orthosteric binding pocket.

4. Heavy Atom & Side-Chain Rebuilding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Invokes ``pdbfixer`` to detect and rebuild missing side-chain heavy atoms and unresolved
residues within the receptor transmembrane bundle, outputting ``receptor_fixed.pdb``.

5. Receptor Topology Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Executes ``gmx pdb2gmx`` using the **Amber99SB-ILDN** force field and the **TIP3P** water
model. This step recognizes the critical Cys140–Cys217 disulfide bridge connecting TM3
to ECL2 and outputs:

- ``conf.gro``: Receptor coordinate structure file.
- ``topol.top``: Master GROMACS system topology.
- ``posre.itp``: Position restraints for heavy backbone atoms.

6. Ligand Conformer Generation & Targeted Docking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

7. Ligand Parameterization (GAFF2 / ACPYPE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ACPYPE parameterizes the docked ligand using the General Amber Force Field 2 (GAFF2)
and Gasteiger partial atomic charges, producing ``ligand_docked.acpype/``.

8. Amphipol A8-35 Synthesis & Parameterization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``build_amphipol.py`` constructs the Amphipol A8-35 chain matching the
experimental 35:25:40 monomer stoichiometry, embeds and minimizes the 3D conformer,
and invokes ACPYPE to generate GAFF2 parameters (``apol.acpype/``).

9. Complex Assembly & Topology Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``assemble_system.py`` combines all components into ``complex_amphipol.gro``:

- Determines the receptor's transmembrane center of mass (:math:`X=12.01, Y=14.01, Z=12.89\text{ nm}`).
- Arranges 6 Amphipol A8-35 chains in an annular belt (:math:`R \approx 2.65\text{ nm}`)
  surrounding the 7TM bundle, with alternating :math:`\pm 0.3\text{ nm}` vertical staggering.
  Chains are rotated so that hydrophobic octyl and isopropyl chains face inward and
  hydrophilic carboxylates face outward into water.
- Integrates the docked ligand coordinates.
- Modularizes topologies by extracting ``ligand.itp`` and ``apol.itp`` and merges all
  GAFF2 atomtypes into a deduplicated ``extra_atomtypes.itp``.
- Updates ``topol.top`` with all inclusions and molecule counts.

10. Index Group Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``make_index.py`` generates ``index.ndx`` containing specific groups:

- ``[ Binding_Pocket ]``: C-alpha atoms of orthosteric pocket residues (Asp147, Tyr148,
  Met151, Trp293, Val300, Tyr326).
- ``[ Ligand ]``: All atoms of 12-bromo-7-hydroxymitragynine.
- ``[ Solute_Complex ]``: All protein, amphipol, and ligand atoms for temperature coupling.

11. Umbrella Sampling Window Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``setup_umbrella_windows.py`` initializes 22 template directories across the
reaction coordinate range:

.. math::

   \xi_i \in [0.40, 0.50, 0.60, \dots, 2.40, 2.50]\text{ nm}

Each window folder receives a customized ``umbrella.mdp`` with the appropriate reference
distance ``pull-coord1-init = <xi_i>``.

12. Binary Compilation & Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compiles ``run.tpr`` using ``gmx grompp`` and ``em.mdp`` to confirm zero topology syntax
errors, correct atom exclusions, and charge consistency.

Simulation Protocols
====================

1. Energy Minimization (``em.mdp``)
-----------------------------------

Performs steepest descent minimization (:math:`F_{\text{max}} < 1000.0\text{ kJ/mol/nm}`)
to relax any remaining contact overlaps between the receptor, ligand, and amphipol belt:

.. code-block:: bash

   gmx mdrun -v -deffnm em

2. Explicit Water Solvation & Neutralization
--------------------------------------------

The complex is solvated using an explicit 3-site water model (TIP3P) and neutralized
with physiological counterions (0.15 M NaCl).

Explicit Water Mechanics in GROMACS:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running ``gmx solvate``:

- **``-cp box.gro`` (Configuration Protein/Solute)**: Specifies the solute structure
  containing the receptor, docked ligand, and amphipol belt.
- **``-cs spc216.gro`` (Configuration Solvent)**: Specifies the explicit solvent template.
  GROMACS bundles pre-equilibrated coordinate lattices in its shared library directory
  (``$GMXDATA/top/``). You **do not** need to download or provide external water PDB/GRO files;
  GROMACS resolves ``spc216.gro`` automatically from its installation path. (If ``-cs`` is
  omitted, GROMACS defaults to ``spc216.gro``).
- **Model Parameter Inheritance**: While ``spc216.gro`` provides the spatial 3-site coordinate
  geometry, the actual interaction parameters (charges, bond lengths, angles, and Lennard-Jones
  coefficients) are inherited from the ``#include "amber99sb-ildn.ff/tip3p.itp"`` directive
  configured in ``topol.top`` during receptor preparation (``pdb2gmx -water tip3p``).
- **Alternative Explicit Models**: If using a 4-site model (e.g., TIP4P or TIP4P-Ew) or 5-site
  model (TIP5P), pass the corresponding bundled coordinate file: ``-cs tip4p.gro`` or ``-cs tip5p.gro``.

Execution Commands:
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Step A: Define periodic boundary box with 1.5 nm clearance for ligand unbinding
   gmx editconf -f complex_amphipol.gro -o box.gro -c -d 1.5 -bt dodecahedron

   # Step B: Solvate with explicit 3-site water (updates [ molecules ] in topol.top)
   gmx solvate -cp box.gro -cs spc216.gro -o solv.gro -p topol.top

   # Step C: Compile ionization input
   gmx grompp -f em.mdp -c solv.gro -p topol.top -o ions.tpr -maxwarn 1

   # Step D: Replace solvent molecules with ions (0.15 M NaCl + counterions for net neutrality)
   echo "SOL" | gmx genion -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15

   # Step E: Re-minimize the solvated, ionized system to relax water and ion positions
   gmx grompp -f em.mdp -c solv_ions.gro -p topol.top -o em.tpr
   gmx mdrun -v -deffnm em

3. NVT and NPT Equilibration (``nvt.mdp``, ``npt.mdp``)
-------------------------------------------------------

Equilibrates the solvent and amphipol belt around the position-restrained receptor and
ligand heavy atoms:

.. code-block:: bash

   # NVT Equilibration (100 ps, 310 K)
   gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -n index.ndx -o nvt.tpr
   gmx mdrun -v -deffnm nvt

   # NPT Equilibration (100 ps, 1 bar, isotropic)
   gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr
   gmx mdrun -v -deffnm npt

4. Steered Molecular Dynamics (SMD) Pulling (``pull.mdp``)
----------------------------------------------------------

Pulls the ligand out of the orthosteric binding pocket along the center-of-mass distance
vector at a pulling rate of :math:`v = 0.002\text{ nm/ps}` over 1000 ps:

.. code-block:: bash

   gmx grompp -f pull.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -n index.ndx -o pull.tpr
   gmx mdrun -v -deffnm pull -pf pullf.xvg -px pullx.xvg

5. Umbrella Sampling Windows & WHAM Analysis
--------------------------------------------

Extracts frames corresponding to each window reference distance from ``pullx.xvg`` and
runs production sampling:

.. code-block:: bash

   # Extract window starting frames and generate window TPRs
   python3 setup_umbrella_windows.py

   # For each window (window_0.40 through window_2.50):
   # cd window_0.40
   # gmx grompp -f umbrella.mdp -c conf_0.40.gro -r conf_0.40.gro -p ../topol.top -n ../index.ndx -o umbrella.tpr
   # gmx mdrun -v -deffnm umbrella

   # Calculate binding free energy profile (PMF) via WHAM:
   gmx wham -ix tpr_files.dat -if pullf_files.dat -o profile.xvg -hist histo.xvg -unit kJ

File Manifest
=============

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - File / Directory
     - Purpose
   * - ``setup_mor_simulation.sh``
     - Master automation script executing stages 1 through 12.
   * - ``cleanup_mor_simulation.sh``
     - Cleans generated simulation artifacts and obsolete legacy files.
   * - ``6DDF.pdb``
     - Cryo-EM structure of active human μOR complexed with Gi and DAMGO.
   * - ``extract_chain.py``
     - Isolates receptor (Chain R) and pocket reference DAMGO (Chain D).
   * - ``dock_ligand.py``
     - Generates 3D ligand conformer and performs targeted docking into Asp147.
   * - ``build_amphipol.py``
     - Synthesizes and parameterizes Amphipol A8-35 chains using ACPYPE.
   * - ``assemble_system.py``
     - Places 6 A8-35 chains around the TM bundle, merges coordinates, and updates topology.
   * - ``make_index.py``
     - Builds custom GROMACS index groups for Binding_Pocket and Ligand.
   * - ``setup_umbrella_windows.py``
     - Sets up umbrella sampling window directories from pulling trajectory.
   * - ``complex_amphipol.gro``
     - Assembled coordinate file (MOR + 12-bromo-7-OH-mitragynine + 6 Amphipols).
   * - ``extra_atomtypes.itp``
     - Deduplicated GAFF2 non-bonded atom types for ligand and amphipols.
   * - ``ligand.itp``
     - Molecular topology for 12-bromo-7-hydroxymitragynine.
   * - ``apol.itp``
     - Molecular topology for Amphipol A8-35.
   * - ``topol.top``
     - Master GROMACS topology file for the assembled system.
   * - ``posre.itp``
     - Position restraint definitions for receptor backbone and heavy atoms.
   * - ``em.mdp``
     - GROMACS parameter file for steepest descent energy minimization.
   * - ``nvt.mdp``
     - GROMACS parameter file for 100 ps NVT equilibration at 310 K.
   * - ``npt.mdp``
     - GROMACS parameter file for 100 ps NPT equilibration at 1 bar.
   * - ``pull.mdp``
     - GROMACS parameter file for steered MD ligand unbinding pulling.
   * - ``umbrella.mdp``
     - GROMACS parameter file template for static harmonic umbrella sampling.
   * - ``plumed_binding.dat``
     - PLUMED definition for the ligand-binding pocket distance collective variable.
   * - ``run.tpr``
     - Portable binary run input compiled and validated by GROMACS grompp.

Prerequisites & Requirements
============================

System Binaries:
----------------

- **GROMACS** (version 2021 or higher, built with PLUMED support if using ``plumed_binding.dat``)
- **AmberTools** (or ACPYPE bundled Amber binaries)
- **wget** (for automated structure retrieval)

Python Dependencies:
--------------------

Installed automatically into ``.venv`` by ``setup_mor_simulation.sh``:

- ``rdkit``
- ``acpype``
- ``pdbfixer``
- ``openmm``
- ``numpy``

Quickstart
==========

To run the complete automated setup from scratch:

.. code-block:: bash

   chmod +x setup_mor_simulation.sh
   ./setup_mor_simulation.sh

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
