# 05_dock_ligand/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(LIGAND_DOCKED_PDB "${CMAKE_CURRENT_BINARY_DIR}/ligand_docked.pdb")

add_custom_command(
    OUTPUT "${LIGAND_DOCKED_PDB}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/dock_ligand.py"
        --damgo "${DAMGO_PDB}"
        --receptor "${RECEPTOR_FIXED_PDB}"
        --output "${LIGAND_DOCKED_PDB}"
    DEPENDS 02_extract_chains 03_rebuild_atoms
            "${DAMGO_PDB}" "${RECEPTOR_FIXED_PDB}"
            "${CMAKE_CURRENT_SOURCE_DIR}/dock_ligand.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Docking 12-bromo-7-hydroxymitragynine into orthosteric pocket"
)

add_custom_target(05_dock_ligand DEPENDS "${LIGAND_DOCKED_PDB}")
set(LIGAND_DOCKED_PDB "${LIGAND_DOCKED_PDB}" PARENT_SCOPE)
