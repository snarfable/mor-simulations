# 09_em_complex/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(COMPLEX_EM_TPR "${CMAKE_CURRENT_BINARY_DIR}/complex-em.tpr")
set(COMPLEX_EM_GRO "${CMAKE_CURRENT_BINARY_DIR}/complex-em.gro")

add_custom_command(
    OUTPUT "${COMPLEX_EM_TPR}" "${COMPLEX_EM_GRO}"
    COMMAND ${CMAKE_COMMAND} -E copy "${ASSEMBLED_TOP}" "${CMAKE_CURRENT_BINARY_DIR}/topol.top"
    COMMAND ${CMAKE_COMMAND} -E copy "${EXTRA_ATOMTYPES_ITP}" "${CMAKE_CURRENT_BINARY_DIR}/extra_atomtypes.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${LIGAND_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/ligand.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${APOL_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/apol.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${POSRE_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/posre.itp"
    COMMAND ${GMX_EXECUTABLE} grompp -f "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" -c "${COMPLEX_GRO}" -p "${CMAKE_CURRENT_BINARY_DIR}/topol.top" -o "${COMPLEX_EM_TPR}" ${GMX_GROMPP_EXTRA_ARGS}
    COMMAND ${GMX_EXECUTABLE} mdrun -v -deffnm complex-em -s "${COMPLEX_EM_TPR}" -c "${COMPLEX_EM_GRO}"
    DEPENDS 08_assemble_system
            "${COMPLEX_GRO}" "${ASSEMBLED_TOP}" "${EXTRA_ATOMTYPES_ITP}"
            "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}"
            "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" "${GMX_EXECUTABLE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Compiling and running initial vacuum energy minimization with gmx grompp/mdrun"
)

add_custom_target(09_em_complex DEPENDS "${COMPLEX_EM_TPR}" "${COMPLEX_EM_GRO}")
set(COMPLEX_EM_TPR "${COMPLEX_EM_TPR}" PARENT_SCOPE)
set(COMPLEX_EM_GRO "${COMPLEX_EM_GRO}" PARENT_SCOPE)
