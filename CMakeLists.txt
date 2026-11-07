# CMakeLists.txt: Top-level build file orchestrating the MOR simulation pipeline
cmake_minimum_required(VERSION 3.20)
project(mor_simulation C CXX)

# Prefer local virtual environment if present
if(EXISTS "${CMAKE_SOURCE_DIR}/.venv/bin")
    list(PREPEND CMAKE_PROGRAM_PATH "${CMAKE_SOURCE_DIR}/.venv/bin")
    set(Python3_ROOT_DIR "${CMAKE_SOURCE_DIR}/.venv")
endif()

# Discover required toolchains and interpreters
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_program(PDBFIXER_EXECUTABLE NAMES pdbfixer HINTS "${CMAKE_SOURCE_DIR}/.venv/bin" DOC "PDBFixer executable")
find_program(ACPYPE_EXECUTABLE NAMES acpype HINTS "${CMAKE_SOURCE_DIR}/.venv/bin" DOC "ACPYPE executable")
find_program(WGET_EXECUTABLE NAMES wget curl DOC "Downloader executable")

# Fetch and build GROMACS in-source
include(FetchContent)

set(GMX_PYTHON_PACKAGE ON CACHE BOOL "" FORCE)
set(GMXAPI_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GMXAPI ON CACHE BOOL "" FORCE)
set(GMX_BUILD_OWN_FFTW ON CACHE BOOL "" FORCE)
set(GMX_TMPI ON CACHE BOOL "" FORCE)
set(GMX_OPENMP ON CACHE BOOL "" FORCE)

FetchContent_Declare(
    gromacs
    GIT_REPOSITORY https://github.com/gromacs/gromacs.git
    GIT_TAG main
    PATCH_COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/cmake/patch_gromacs.py" "<SOURCE_DIR>"
)
FetchContent_MakeAvailable(gromacs)

set(GMX_EXECUTABLE gmx)

message(STATUS "Using Python:    ${Python3_EXECUTABLE}")
message(STATUS "Using GROMACS:   Target ${GMX_EXECUTABLE} (FetchContent)")
message(STATUS "Using PDBFixer:  ${PDBFIXER_EXECUTABLE}")
message(STATUS "Using ACPYPE:    ${ACPYPE_EXECUTABLE}")

# Add step subdirectories in pipeline order
add_subdirectory(01_download_pdb)
add_subdirectory(02_extract_chains)
add_subdirectory(03_rebuild_atoms)
add_subdirectory(04_receptor_topology)
add_subdirectory(05_dock_ligand)
add_subdirectory(06_ligand_params)
add_subdirectory(07_build_amphipol)
add_subdirectory(08_assemble_system)
add_subdirectory(09_em_complex)
add_subdirectory(10_solvate)
add_subdirectory(11_em_solv)
add_subdirectory(12_make_index)
add_subdirectory(13_nvt)
add_subdirectory(14_setup_umbrella)
add_subdirectory(15_production)

# Master pipeline target
add_custom_target(mor_pipeline ALL
    DEPENDS
        01_download_pdb
        02_extract_chains
        03_rebuild_atoms
        04_receptor_topology
        05_dock_ligand
        06_ligand_params
        07_build_amphipol
        08_assemble_system
        09_em_complex
        10_solvate
        11_em_solv
        12_make_index
        13_nvt
        14_setup_umbrella
        15_production
    COMMENT "Complete MOR simulation setup and equilibration pipeline successfully built!"
)
