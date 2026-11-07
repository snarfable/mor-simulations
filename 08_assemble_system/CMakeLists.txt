# 08_assemble_system/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(COMPLEX_GRO "${CMAKE_CURRENT_BINARY_DIR}/complex_amphipol.gro")
set(ASSEMBLED_TOP "${CMAKE_CURRENT_BINARY_DIR}/topol.top")
set(EXTRA_ATOMTYPES_ITP "${CMAKE_CURRENT_BINARY_DIR}/extra_atomtypes.itp")
set(LIGAND_ITP_OUT "${CMAKE_CURRENT_BINARY_DIR}/ligand.itp")
set(APOL_ITP_OUT "${CMAKE_CURRENT_BINARY_DIR}/apol.itp")
set(POSRE_ITP_OUT "${CMAKE_CURRENT_BINARY_DIR}/posre.itp")

add_custom_command(
    OUTPUT "${COMPLEX_GRO}" "${ASSEMBLED_TOP}" "${EXTRA_ATOMTYPES_ITP}" "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}"
    COMMAND ${CMAKE_COMMAND} -E copy "${RECEPTOR_TOPOL_TOP}" "${ASSEMBLED_TOP}"
    COMMAND ${CMAKE_COMMAND} -E copy "${RECEPTOR_POSRE_ITP}" "${POSRE_ITP_OUT}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/assemble_system.py"
        --rec-gro "${RECEPTOR_CONF_GRO}"
        --lig-gro "${LIGAND_GRO}"
        --apol-gro "${APOL_GRO}"
        --lig-itp "${LIGAND_ITP}"
        --apol-itp "${APOL_ITP}"
        --out-gro "${COMPLEX_GRO}"
        --top-file "${ASSEMBLED_TOP}"
    DEPENDS 04_receptor_topology 06_ligand_params 07_build_amphipol python_dependencies
            "${RECEPTOR_CONF_GRO}" "${RECEPTOR_TOPOL_TOP}" "${RECEPTOR_POSRE_ITP}"
            "${LIGAND_GRO}" "${LIGAND_ITP}"
            "${APOL_GRO}" "${APOL_ITP}"
            "${CMAKE_CURRENT_SOURCE_DIR}/assemble_system.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Assembling MOR-Amphipol-Ligand complex and integrating topologies"
)

add_custom_target(08_assemble_system DEPENDS python_dependencies "${COMPLEX_GRO}" "${ASSEMBLED_TOP}" "${EXTRA_ATOMTYPES_ITP}" "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}")
set(COMPLEX_GRO "${COMPLEX_GRO}" PARENT_SCOPE)
set(ASSEMBLED_TOP "${ASSEMBLED_TOP}" PARENT_SCOPE)
set(EXTRA_ATOMTYPES_ITP "${EXTRA_ATOMTYPES_ITP}" PARENT_SCOPE)
set(LIGAND_ITP_OUT "${LIGAND_ITP_OUT}" PARENT_SCOPE)
set(APOL_ITP_OUT "${APOL_ITP_OUT}" PARENT_SCOPE)
set(POSRE_ITP_OUT "${POSRE_ITP_OUT}" PARENT_SCOPE)
