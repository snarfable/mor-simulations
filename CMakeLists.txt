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
get_filename_component(Python3_BIN_DIR "${Python3_EXECUTABLE}" DIRECTORY)

# Required Python packages for pipeline and GROMACS gmxapi / python bindings
set(REQUIRED_PYTHON_PACKAGES
    rdkit
    mpi4py
    pdbfixer
    openmm
    numpy
    pybind11
    pytest
    acpype
)

# Target to install/verify Python dependencies
add_custom_target(python_dependencies
    COMMAND ${Python3_EXECUTABLE} -m pip install ${REQUIRED_PYTHON_PACKAGES}
    COMMENT "Installing required Python dependencies (${REQUIRED_PYTHON_PACKAGES})"
)
add_custom_target(install_python_dependencies DEPENDS python_dependencies)

# Configure-time check: verify if modules are already installed, install if missing
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import rdkit, mpi4py, pdbfixer, openmm, numpy, pybind11, pytest, acpype"
    RESULT_VARIABLE _py_check_res
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT _py_check_res EQUAL 0)
    message(STATUS "Required Python packages missing. Installing via pip...")
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -m pip install ${REQUIRED_PYTHON_PACKAGES}
        RESULT_VARIABLE _pip_install_res
    )
    if(NOT _pip_install_res EQUAL 0)
        message(WARNING "Failed to install some Python packages via pip. Please ensure network connectivity or install manually.")
    endif()
endif()

find_program(PDBFIXER_EXECUTABLE NAMES pdbfixer HINTS "${Python3_BIN_DIR}" "${CMAKE_SOURCE_DIR}/.venv/bin" DOC "PDBFixer executable")
find_program(ACPYPE_EXECUTABLE NAMES acpype HINTS "${Python3_BIN_DIR}" "${CMAKE_SOURCE_DIR}/.venv/bin" DOC "ACPYPE executable")
find_program(WGET_EXECUTABLE NAMES wget curl DOC "Downloader executable")

# Fetch and build GROMACS in-source
include(FetchContent)

set(GMX_PYTHON_PACKAGE ON CACHE BOOL "" FORCE)
set(GMXAPI_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GMXAPI ON CACHE BOOL "" FORCE)
set(GMX_BUILD_OWN_FFTW ON CACHE BOOL "" FORCE)
set(GMX_TMPI ON CACHE BOOL "" FORCE)
set(GMX_OPENMP ON CACHE BOOL "" FORCE)

# GPU acceleration and mdrun runtime flags
if(NOT DEFINED GMX_GPU OR GMX_GPU STREQUAL "ON")
    set(GMX_GPU OFF CACHE STRING "Enable GPU acceleration in GROMACS (CUDA, OpenCL, SYCL, HIP, or OFF)" FORCE)
else()
    set(GMX_GPU "${GMX_GPU}" CACHE STRING "Enable GPU acceleration in GROMACS (CUDA, OpenCL, SYCL, HIP, or OFF)")
endif()
set_property(CACHE GMX_GPU PROPERTY STRINGS OFF CUDA OpenCL SYCL HIP)

set(GMX_MDRUN_GPU_FLAGS "" CACHE STRING "GPU-related flags to pass to gmx mdrun (e.g. '-nb gpu -pme gpu -pmefft gpu -bonded gpu -update gpu')")

# If GMX_GPU is enabled (not OFF) and user did not specify custom GMX_MDRUN_GPU_FLAGS, set default GPU offload flags
if(NOT GMX_GPU STREQUAL "OFF" AND NOT GMX_MDRUN_GPU_FLAGS)
    set(GMX_MDRUN_GPU_FLAGS "-nb gpu -pme gpu -pmefft gpu -bonded gpu -update gpu" CACHE STRING "GPU-related flags to pass to gmx mdrun" FORCE)
endif()

separate_arguments(GMX_MDRUN_GPU_ARGS NATIVE_COMMAND "${GMX_MDRUN_GPU_FLAGS}")

FetchContent_Declare(
    gromacs
    GIT_REPOSITORY https://github.com/gromacs/gromacs.git
    GIT_TAG main
    PATCH_COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/cmake/patch_gromacs.py" "<SOURCE_DIR>"
)
FetchContent_MakeAvailable(gromacs)

set(GMX_EXECUTABLE gmx)

message(STATUS "Using Python:            ${Python3_EXECUTABLE}")
message(STATUS "Using GROMACS:           Target ${GMX_EXECUTABLE} (FetchContent)")
message(STATUS "Using PDBFixer:          ${PDBFIXER_EXECUTABLE}")
message(STATUS "Using ACPYPE:            ${ACPYPE_EXECUTABLE}")
message(STATUS "GMX_GPU:                 ${GMX_GPU}")
message(STATUS "GMX_MDRUN_GPU_FLAGS:     ${GMX_MDRUN_GPU_FLAGS}")

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
        python_dependencies
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
