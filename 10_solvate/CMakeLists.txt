# 10_solvate/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(BOX_GRO "${CMAKE_CURRENT_BINARY_DIR}/box.gro")
set(SOLV_GRO "${CMAKE_CURRENT_BINARY_DIR}/solv.gro")
set(IONS_TPR "${CMAKE_CURRENT_BINARY_DIR}/ions.tpr")
set(SOLV_IONS_GRO "${CMAKE_CURRENT_BINARY_DIR}/solv-ions.gro")
set(SOLV_TOP "${CMAKE_CURRENT_BINARY_DIR}/topol.top")

add_custom_command(
    OUTPUT "${BOX_GRO}" "${SOLV_GRO}" "${IONS_TPR}" "${SOLV_IONS_GRO}" "${SOLV_TOP}"
    COMMAND ${CMAKE_COMMAND} -E copy "${ASSEMBLED_TOP}" "${SOLV_TOP}"
    COMMAND ${CMAKE_COMMAND} -E copy "${EXTRA_ATOMTYPES_ITP}" "${CMAKE_CURRENT_BINARY_DIR}/extra_atomtypes.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${LIGAND_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/ligand.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${APOL_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/apol.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${POSRE_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/posre.itp"
    COMMAND ${GMX_EXECUTABLE} editconf -f "${COMPLEX_EM_GRO}" -o "${BOX_GRO}" -c -d 1.5 -bt dodecahedron
    COMMAND ${GMX_EXECUTABLE} solvate -cp "${BOX_GRO}" -cs spc216.gro -o "${SOLV_GRO}" -p "${SOLV_TOP}"
    COMMAND ${GMX_EXECUTABLE} grompp -f "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" -c "${SOLV_GRO}" -p "${SOLV_TOP}" -o "${IONS_TPR}" -maxwarn 1
    COMMAND echo SOL | ${GMX_EXECUTABLE} genion -s ${IONS_TPR} -o ${SOLV_IONS_GRO} -p ${SOLV_TOP} -pname NA -nname CL -neutral -conc 0.15
    DEPENDS 09_em_complex
            "${COMPLEX_EM_GRO}" "${ASSEMBLED_TOP}" "${EXTRA_ATOMTYPES_ITP}"
            "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}"
            "${CMAKE_CURRENT_SOURCE_DIR}/em.mdp" "${GMX_EXECUTABLE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Generating dodecahedron box, explicit solvation, and counterion neutralization"
)

add_custom_target(10_solvate DEPENDS "${BOX_GRO}" "${SOLV_GRO}" "${IONS_TPR}" "${SOLV_IONS_GRO}" "${SOLV_TOP}")
set(SOLV_IONS_GRO "${SOLV_IONS_GRO}" PARENT_SCOPE)
set(SOLV_TOP "${SOLV_TOP}" PARENT_SCOPE)
