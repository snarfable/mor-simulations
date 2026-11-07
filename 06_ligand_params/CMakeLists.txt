# 06_ligand_params/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(LIGAND_GRO "${CMAKE_CURRENT_BINARY_DIR}/ligand_docked.acpype/ligand_docked_GMX.gro")
set(LIGAND_ITP "${CMAKE_CURRENT_BINARY_DIR}/ligand_docked.acpype/ligand_docked_GMX.itp")

add_custom_command(
    OUTPUT "${LIGAND_GRO}" "${LIGAND_ITP}"
    COMMAND ${ACPYPE_EXECUTABLE} -i "${LIGAND_DOCKED_PDB}" -c gas -n 0 -a gaff2 -b ligand_docked
    DEPENDS 05_dock_ligand python_dependencies "${LIGAND_DOCKED_PDB}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Parameterizing docked ligand using ACPYPE (GAFF2)"
)

add_custom_target(06_ligand_params DEPENDS python_dependencies "${LIGAND_GRO}" "${LIGAND_ITP}")
set(LIGAND_GRO "${LIGAND_GRO}" PARENT_SCOPE)
set(LIGAND_ITP "${LIGAND_ITP}" PARENT_SCOPE)
