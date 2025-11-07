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

if(NOT DEFINED NT_FAILFAST_SANITIZER)
  set(_NT_SANITIZER_DEFAULT ON)
  if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(_NT_SANITIZER_DEFAULT OFF)
  endif()
  set(NT_FAILFAST_SANITIZER ${_NT_SANITIZER_DEFAULT} CACHE BOOL "Enable fail-fast sanitizer instrumentation" FORCE)
else()
  set(NT_FAILFAST_SANITIZER ${NT_FAILFAST_SANITIZER} CACHE BOOL "Enable fail-fast sanitizer instrumentation" FORCE)
endif()

if(NOT DEFINED NT_FAILFAST_LINK_ENFORCE)
  set(NT_FAILFAST_LINK_ENFORCE ON CACHE BOOL "Force fail-fast linker guard flags" FORCE)
else()
  set(NT_FAILFAST_LINK_ENFORCE ${NT_FAILFAST_LINK_ENFORCE} CACHE BOOL "Force fail-fast linker guard flags" FORCE)
endif()

if(NOT DEFINED NT_FAILFAST_LINK_FLAGS)
  set(NT_FAILFAST_LINK_FLAGS "/guard:ehcont;/DYNAMICBASE;/LTCG;/Brepro" CACHE STRING "Fail-fast linker guard flags for Windows targets" FORCE)
endif()

if(NT_FAILFAST_SANITIZER)
  set(_NT_SANITIZER_FLAGS "-fsanitize=address -fno-omit-frame-pointer")
  set(_NT_SANITIZER_LINK_FLAGS "-fsanitize=address")
  foreach(_lang C CXX)
    set(CMAKE_${_lang}_FLAGS "${CMAKE_${_lang}_FLAGS} ${_NT_SANITIZER_FLAGS}")
    set(CMAKE_${_lang}_FLAGS_DEBUG "${CMAKE_${_lang}_FLAGS_DEBUG} ${_NT_SANITIZER_FLAGS}")
    set(CMAKE_${_lang}_FLAGS_RELEASE "${CMAKE_${_lang}_FLAGS_RELEASE} ${_NT_SANITIZER_FLAGS}")
  endforeach()
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${_NT_SANITIZER_LINK_FLAGS}")
endif()

if(NT_FAILFAST_LINK_ENFORCE)
  string(REPLACE ";" " " _nt_link_guard_str "${NT_FAILFAST_LINK_FLAGS}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${_nt_link_guard_str}")
endif()
