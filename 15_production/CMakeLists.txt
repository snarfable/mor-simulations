# 15_production/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(PRODUCTION_TEMPLATES_DONE "${CMAKE_CURRENT_BINARY_DIR}/production_templates.done")

add_custom_command(
    OUTPUT "${PRODUCTION_TEMPLATES_DONE}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/npt.mdp" "${CMAKE_CURRENT_BINARY_DIR}/npt.mdp"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/pull.mdp" "${CMAKE_CURRENT_BINARY_DIR}/pull.mdp"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/awh.mdp" "${CMAKE_CURRENT_BINARY_DIR}/awh.mdp"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/md.mdp" "${CMAKE_CURRENT_BINARY_DIR}/md.mdp"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/plumed.dat" "${CMAKE_CURRENT_BINARY_DIR}/plumed.dat"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/plumed_binding.dat" "${CMAKE_CURRENT_BINARY_DIR}/plumed_binding.dat"
    COMMAND ${CMAKE_COMMAND} -E touch "${PRODUCTION_TEMPLATES_DONE}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/npt.mdp"
            "${CMAKE_CURRENT_SOURCE_DIR}/pull.mdp"
            "${CMAKE_CURRENT_SOURCE_DIR}/awh.mdp"
            "${CMAKE_CURRENT_SOURCE_DIR}/md.mdp"
            "${CMAKE_CURRENT_SOURCE_DIR}/plumed.dat"
            "${CMAKE_CURRENT_SOURCE_DIR}/plumed_binding.dat"
    COMMENT "Setting up production simulation parameter templates and PLUMED configs"
)

add_custom_target(15_production DEPENDS "${PRODUCTION_TEMPLATES_DONE}")
