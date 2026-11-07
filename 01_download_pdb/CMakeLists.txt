# 01_download_pdb/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

set(PDB_6DDF "${CMAKE_CURRENT_BINARY_DIR}/6DDF.pdb")

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/6DDF.pdb")
    add_custom_command(
        OUTPUT "${PDB_6DDF}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/6DDF.pdb" "${PDB_6DDF}"
        DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/6DDF.pdb"
        COMMENT "Copying 6DDF.pdb to build directory"
    )
else()
    add_custom_command(
        OUTPUT "${PDB_6DDF}"
        COMMAND ${WGET_EXECUTABLE} -q -c https://files.rcsb.org/download/6DDF.pdb -O "${PDB_6DDF}"
        COMMENT "Downloading Mu-Opioid Receptor Structure (PDB: 6DDF)"
    )
endif()

add_custom_target(01_download_pdb DEPENDS "${PDB_6DDF}")
set(PDB_6DDF "${PDB_6DDF}" PARENT_SCOPE)
