# 11_em_solv/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(SOLV_EM_TPR "${CMAKE_CURRENT_BINARY_DIR}/solv-em.tpr")
set(SOLV_EM_GRO "${CMAKE_CURRENT_BINARY_DIR}/solv-em.gro")

add_custom_command(
    OUTPUT "${SOLV_EM_TPR}" "${SOLV_EM_GRO}"
    COMMAND ${CMAKE_COMMAND} -E copy "${SOLV_TOP}" "${CMAKE_CURRENT_BINARY_DIR}/topol.top"
    COMMAND ${CMAKE_COMMAND} -E copy "${EXTRA_ATOMTYPES_ITP}" "${CMAKE_CURRENT_BINARY_DIR}/extra_atomtypes.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${LIGAND_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/ligand.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${APOL_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/apol.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${POSRE_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/posre.itp"
    COMMAND ${GMX_EXECUTABLE} grompp -f "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" -c "${SOLV_IONS_GRO}" -p "${CMAKE_CURRENT_BINARY_DIR}/topol.top" -o "${SOLV_EM_TPR}"
    COMMAND ${GMX_EXECUTABLE} mdrun -v -deffnm solv-em -s "${SOLV_EM_TPR}" -c "${SOLV_EM_GRO}"
    DEPENDS 10_solvate
            "${SOLV_IONS_GRO}" "${SOLV_TOP}" "${EXTRA_ATOMTYPES_ITP}"
            "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}"
            "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" "${GMX_EXECUTABLE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Energy minimizing solvated and neutralized system"
)

add_custom_target(11_em_solv DEPENDS "${SOLV_EM_TPR}" "${SOLV_EM_GRO}")
set(SOLV_EM_TPR "${SOLV_EM_TPR}" PARENT_SCOPE)
set(SOLV_EM_GRO "${SOLV_EM_GRO}" PARENT_SCOPE)
