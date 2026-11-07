# 12_make_index/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(INDEX_NDX "${CMAKE_CURRENT_BINARY_DIR}/index.ndx")

add_custom_command(
    OUTPUT "${INDEX_NDX}"
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/make_index.py" "${SOLV_EM_GRO}" "${INDEX_NDX}"
    DEPENDS 11_em_solv python_dependencies "${SOLV_EM_GRO}" "${CMAKE_CURRENT_SOURCE_DIR}/make_index.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Generating GROMACS index groups for pulling and umbrella sampling"
)

add_custom_target(12_make_index DEPENDS python_dependencies "${INDEX_NDX}")
set(INDEX_NDX "${INDEX_NDX}" PARENT_SCOPE)
