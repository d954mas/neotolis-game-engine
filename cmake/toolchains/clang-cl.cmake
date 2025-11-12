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

get_filename_component(_LLVM_BINDIR "${CLANG_CL}" DIRECTORY)
set(_LLVM_HINT_DIRS "${_LLVM_BINDIR}" "$ENV{LLVM_HOME}/bin" "C:/Program Files/LLVM/bin")

# --- archiver ---
find_program(LLVM_AR NAMES llvm-ar
             HINTS ${_LLVM_HINT_DIRS}
             ENV PATH REQUIRED)
set(CMAKE_AR "${LLVM_AR}" CACHE FILEPATH "Archiver" FORCE)
set(CMAKE_C_COMPILER_AR "${LLVM_AR}" CACHE FILEPATH "C archiver" FORCE)
set(CMAKE_CXX_COMPILER_AR "${LLVM_AR}" CACHE FILEPATH "C++ archiver" FORCE)

# --- ranlib ---
find_program(LLVM_RANLIB NAMES llvm-ranlib
             HINTS ${_LLVM_HINT_DIRS}
             ENV PATH REQUIRED)
set(CMAKE_RANLIB "${LLVM_RANLIB}" CACHE FILEPATH "ranlib" FORCE)
set(CMAKE_C_COMPILER_RANLIB "${LLVM_RANLIB}" CACHE FILEPATH "C ranlib" FORCE)
set(CMAKE_CXX_COMPILER_RANLIB "${LLVM_RANLIB}" CACHE FILEPATH "C++ ranlib" FORCE)

# --- linker ---
find_program(LLD_LINK NAMES lld-link
             HINTS ${_LLVM_HINT_DIRS}
             ENV PATH REQUIRED)
set(CMAKE_LINKER "${LLD_LINK}")

# --- resource compiler (optional) ---
find_program(LLVM_RC NAMES llvm-rc rc
             HINTS ${_LLVM_HINT_DIRS}
             ENV PATH)
if(LLVM_RC)
  set(CMAKE_RC_COMPILER "${LLVM_RC}")
endif()

# --- manifest tool (required) ---
find_program(CMAKE_MT NAMES llvm-mt mt
             HINTS ${_LLVM_HINT_DIRS}
             ENV PATH)
if(NOT CMAKE_MT)
  message(FATAL_ERROR "Manifest tool (llvm-mt/mt) not found. Install LLVM or Windows SDK and ensure it is in PATH.")
endif()
set(CMAKE_MANIFEST_TOOL "${CMAKE_MT}" CACHE FILEPATH "Manifest tool" FORCE)
message(STATUS "Using manifest tool: ${CMAKE_MT}")

# NOTE:
# No global warnings, optimizations, or standards here.
# Handle them per-target or in CMakePresets.

include("${CMAKE_CURRENT_LIST_DIR}/../NTFailfastOptions.cmake")

nt_failfast_configure_warning_flags(
  "/Wall;/WX;/permissive-"
  "Fail-fast compile warnings for Windows targets"
)

nt_failfast_configure_sanitizer(
  ON
  OFF
  "Enable fail-fast sanitizer instrumentation"
)

nt_failfast_cache_bool(NT_FAILFAST_LINK_ENFORCE ON "Force fail-fast linker guard flags")

nt_failfast_configure_link_flags(
  "/guard:ehcont;/DYNAMICBASE;/LTCG;/Brepro"
  "/guard:ehcont;/DYNAMICBASE;/LTCG;/Brepro"
  "Fail-fast linker guard flags for Windows targets"
)

if(NT_FAILFAST_SANITIZER)
  message(STATUS "Fail-fast sanitizers are only enabled on Windows release builds using the /MD runtime")
  set(NT_FAILFAST_SANITIZER OFF CACHE BOOL "Enable fail-fast sanitizer instrumentation" FORCE)
endif()

if(NT_FAILFAST_LINK_ENFORCE)
  string(REPLACE ";" " " _nt_link_guard_str "${NT_FAILFAST_LINK_FLAGS}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${_nt_link_guard_str}")
endif()
