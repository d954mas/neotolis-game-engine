# cmake/toolchains/clang-cl.cmake
# Minimal toolchain for clang-cl + lld-link, with mandatory manifest tool.

set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

# --- compilers ---
find_program(CLANG_CL NAMES clang-cl
             HINTS "$ENV{LLVM_HOME}/bin" "C:/Program Files/LLVM/bin"
             ENV PATH REQUIRED)
set(CMAKE_C_COMPILER   "${CLANG_CL}")
set(CMAKE_CXX_COMPILER "${CLANG_CL}")

# --- linker ---
find_program(LLD_LINK NAMES lld-link
             HINTS "$ENV{LLVM_HOME}/bin" "C:/Program Files/LLVM/bin"
             ENV PATH REQUIRED)
set(CMAKE_LINKER "${LLD_LINK}")

# --- resource compiler (optional) ---
find_program(LLVM_RC NAMES llvm-rc rc
             HINTS "$ENV{LLVM_HOME}/bin" "C:/Program Files/LLVM/bin"
             ENV PATH)
if(LLVM_RC)
  set(CMAKE_RC_COMPILER "${LLVM_RC}")
endif()

# --- manifest tool (required) ---
find_program(CMAKE_MT NAMES llvm-mt mt
             HINTS "$ENV{LLVM_HOME}/bin" "C:/Program Files/LLVM/bin"
             ENV PATH)
if(NOT CMAKE_MT)
  message(FATAL_ERROR "Manifest tool (llvm-mt/mt) not found. Install LLVM or Windows SDK and ensure it is in PATH.")
endif()
set(CMAKE_MANIFEST_TOOL "${CMAKE_MT}" CACHE FILEPATH "Manifest tool" FORCE)
message(STATUS "Using manifest tool: ${CMAKE_MT}")

# NOTE:
# No global warnings, optimizations, or standards here.
# Handle them per-target or in CMakePresets.
