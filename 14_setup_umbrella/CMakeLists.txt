# 14_setup_umbrella/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(UMBRELLA_DONE "${CMAKE_CURRENT_BINARY_DIR}/umbrella_setup.done")

add_custom_command(
    OUTPUT "${UMBRELLA_DONE}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/setup_umbrella_windows.py" "pullx.xvg" "${CMAKE_CURRENT_SOURCE_DIR}/umbrella.mdp"
    COMMAND ${CMAKE_COMMAND} -E touch "${UMBRELLA_DONE}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/setup_umbrella_windows.py" "${CMAKE_CURRENT_SOURCE_DIR}/umbrella.mdp"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Initializing umbrella sampling window templates"
)

add_custom_target(14_setup_umbrella DEPENDS "${UMBRELLA_DONE}")
