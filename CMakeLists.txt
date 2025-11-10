cmake_minimum_required(VERSION 3.27)

project(nt_engine
    VERSION 0.1.0
    LANGUAGES C
)

# Destination for packaged artifacts
set(NT_OUTPUT_ROOT "${CMAKE_SOURCE_DIR}/output" CACHE PATH "Root folder for exported build artifacts")

include(cmake/NTArtifacts.cmake)

# Common language settings
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Tooling
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_program(NT_CLANG_TIDY_EXE NAMES clang-tidy)
if(NT_CLANG_TIDY_EXE)
    set(CMAKE_C_CLANG_TIDY
        "${NT_CLANG_TIDY_EXE};-warnings-as-errors=*;--config-file=${CMAKE_SOURCE_DIR}/.clang-tidy"
    )
else()
    message(STATUS "clang-tidy not found; static analysis disabled")
endif()

# Platform detection
if(CMAKE_TARGET_PLATFORM STREQUAL "windows")
    add_compile_definitions(NT_PLATFORM_WINDOWS)
elseif(CMAKE_TARGET_PLATFORM STREQUAL "wasm")
    set(CMAKE_EXECUTABLE_SUFFIX ".html")
    add_compile_definitions(NT_PLATFORM_WASM)
else()
    message(FATAL_ERROR "CMAKE_TARGET_PLATFORM='${CMAKE_TARGET_PLATFORM}' is not supported. Choose from windows, wasm.")
endif()

# Print active build type (handy when using Presets)
message(STATUS "Configuring ${CMAKE_PROJECT_NAME} in ${CMAKE_BUILD_TYPE} mode (${CMAKE_TARGET_PLATFORM})")

# Project toggles
option(NT_PROJECT_SANDBOX "Build the sandbox testbed project" ON)
option(NT_ENABLE_TESTS "Build nt_engine tests" OFF)

# debug flags from presets
set(NT_FAILFAST_WARNING_FLAGS "${NT_FAILFAST_WARNING_FLAGS}" CACHE STRING "Fail-fast compile warnings for all targets")
set(NT_FAILFAST_LINK_FLAGS "${NT_FAILFAST_LINK_FLAGS}" CACHE STRING "Fail-fast linker guard flags for all targets")

add_library(nt_failfast_enforcement INTERFACE)
if(NT_FAILFAST_WARNING_FLAGS)
    target_compile_options(nt_failfast_enforcement INTERFACE
        $<$<COMPILE_LANGUAGE:C>:${NT_FAILFAST_WARNING_FLAGS}>)
endif()
if(NT_FAILFAST_LINK_FLAGS)
    target_link_options(nt_failfast_enforcement INTERFACE ${NT_FAILFAST_LINK_FLAGS})
endif()

# Allow C17-style declaration mixing even when pedantic warnings are enabled
if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    target_compile_options(
        nt_failfast_enforcement INTERFACE
        $<$<COMPILE_LANGUAGE:C>:-Wno-declaration-after-statement>
    )
endif()
set(NT_FAILFAST_ENFORCEMENT_TARGET nt_failfast_enforcement CACHE INTERNAL "Fail-fast compile/link enforcement interface")

# Subprojects
add_subdirectory(engine)

if(NT_PROJECT_SANDBOX)
    add_subdirectory(testbeds/sandbox)
else()
    message(STATUS "Sandbox testbed is disabled. Enable with -DNT_PROJECT_SANDBOX=ON.")
endif()

if(NT_ENABLE_TESTS)
    include(CTest)
    add_subdirectory(tests)
else()
    message(STATUS "Tests are disabled. Configure with -DNT_ENABLE_TESTS=ON or use a *-tests preset to enable them.")
endif()
