# 07_build_amphipol/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(APOL_GRO "${CMAKE_CURRENT_BINARY_DIR}/apol.acpype/apol_GMX.gro")
set(APOL_ITP "${CMAKE_CURRENT_BINARY_DIR}/apol.acpype/apol_GMX.itp")
set(APOL_SINGLE_PDB "${CMAKE_CURRENT_BINARY_DIR}/apol_single.pdb")

add_custom_command(
    OUTPUT "${APOL_GRO}" "${APOL_ITP}" "${APOL_SINGLE_PDB}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/build_amphipol.py" "${APOL_SINGLE_PDB}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/build_amphipol.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Synthesizing and parameterizing Amphipol A8-35"
)

add_custom_target(07_build_amphipol DEPENDS "${APOL_GRO}" "${APOL_ITP}" "${APOL_SINGLE_PDB}")
set(APOL_GRO "${APOL_GRO}" PARENT_SCOPE)
set(APOL_ITP "${APOL_ITP}" PARENT_SCOPE)
