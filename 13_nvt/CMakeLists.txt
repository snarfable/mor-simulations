# 13_nvt/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(SOLV_NVT_TPR "${CMAKE_CURRENT_BINARY_DIR}/solv-nvt.tpr")
set(SOLV_NVT_GRO "${CMAKE_CURRENT_BINARY_DIR}/solv-nvt.gro")

add_custom_command(
    OUTPUT "${SOLV_NVT_TPR}" "${SOLV_NVT_GRO}"
    COMMAND ${CMAKE_COMMAND} -E copy "${SOLV_TOP}" "${CMAKE_CURRENT_BINARY_DIR}/topol.top"
    COMMAND ${CMAKE_COMMAND} -E copy "${EXTRA_ATOMTYPES_ITP}" "${CMAKE_CURRENT_BINARY_DIR}/extra_atomtypes.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${LIGAND_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/ligand.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${APOL_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/apol.itp"
    COMMAND ${CMAKE_COMMAND} -E copy "${POSRE_ITP_OUT}" "${CMAKE_CURRENT_BINARY_DIR}/posre.itp"
    COMMAND ${GMX_EXECUTABLE} grompp -f "${CMAKE_CURRENT_SOURCE_DIR}/nvt.mdp" -c "${SOLV_EM_GRO}" -r "${SOLV_EM_GRO}" -p "${CMAKE_CURRENT_BINARY_DIR}/topol.top" -n "${INDEX_NDX}" -o "${SOLV_NVT_TPR}"
    COMMAND ${GMX_EXECUTABLE} mdrun -v -deffnm solv-nvt -s "${SOLV_NVT_TPR}" -c "${SOLV_NVT_GRO}" ${GMX_MDRUN_GPU_ARGS}
    DEPENDS 11_em_solv 12_make_index
            "${SOLV_EM_GRO}" "${SOLV_TOP}" "${INDEX_NDX}"
            "${EXTRA_ATOMTYPES_ITP}" "${LIGAND_ITP_OUT}" "${APOL_ITP_OUT}" "${POSRE_ITP_OUT}"
            "${CMAKE_CURRENT_SOURCE_DIR}/nvt.mdp" "${GMX_EXECUTABLE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Running NVT equilibration (100 ps, 310 K)"
)

add_custom_target(13_nvt DEPENDS "${SOLV_NVT_TPR}" "${SOLV_NVT_GRO}")
set(SOLV_NVT_TPR "${SOLV_NVT_TPR}" PARENT_SCOPE)
set(SOLV_NVT_GRO "${SOLV_NVT_GRO}" PARENT_SCOPE)
