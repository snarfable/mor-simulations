# 03_rebuild_atoms/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(RECEPTOR_FIXED_PDB "${CMAKE_CURRENT_BINARY_DIR}/receptor_fixed.pdb")

add_custom_command(
    OUTPUT "${RECEPTOR_FIXED_PDB}"
    COMMAND ${PDBFIXER_EXECUTABLE} "${RECEPTOR_PDB}" --output="${RECEPTOR_FIXED_PDB}" --add-atoms=heavy
    DEPENDS 02_extract_chains python_dependencies "${RECEPTOR_PDB}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Rebuilding missing heavy atoms using PDBFixer"
)

add_custom_target(03_rebuild_atoms DEPENDS python_dependencies "${RECEPTOR_FIXED_PDB}")
set(RECEPTOR_FIXED_PDB "${RECEPTOR_FIXED_PDB}" PARENT_SCOPE)
