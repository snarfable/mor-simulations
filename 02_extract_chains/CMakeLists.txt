# 02_extract_chains/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(RECEPTOR_PDB "${CMAKE_CURRENT_BINARY_DIR}/receptor.pdb")
set(DAMGO_PDB "${CMAKE_CURRENT_BINARY_DIR}/damgo.pdb")

add_custom_command(
    OUTPUT "${RECEPTOR_PDB}" "${DAMGO_PDB}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/extract_chain.py" "${PDB_6DDF}" "${RECEPTOR_PDB}" "${DAMGO_PDB}"
    DEPENDS 01_download_pdb "${PDB_6DDF}" "${CMAKE_CURRENT_SOURCE_DIR}/extract_chain.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Extracting Chain R (MOR) and Chain D (DAMGO pocket reference)"
)

add_custom_target(02_extract_chains DEPENDS "${RECEPTOR_PDB}" "${DAMGO_PDB}")
set(RECEPTOR_PDB "${RECEPTOR_PDB}" PARENT_SCOPE)
set(DAMGO_PDB "${DAMGO_PDB}" PARENT_SCOPE)
