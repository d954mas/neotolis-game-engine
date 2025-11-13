cmake_minimum_required(VERSION 3.27)

project(nt_engine
    VERSION 0.1.0
    LANGUAGES C CXX
)

set(FETCHCONTENT_BASE_DIR "${CMAKE_SOURCE_DIR}/.deps")
file(MAKE_DIRECTORY "${FETCHCONTENT_BASE_DIR}")
include(FetchContent)

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
option(NT_PROJECT_SANDBOX "Build the sandbox testbed project" OFF)
option(NT_ENABLE_TESTS "Build nt_engine tests" OFF)
option(NT_ENABLE_WEBGPU "Enable WebGPU integration (Dawn on Windows, Emscripten WebGPU on wasm)" ON)

set(NT_WEBGPU_DISTRIBUTION_TAG "wgpu-v24.0.0.2" CACHE STRING "Git tag/commit for WebGPU-distribution")

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

function(nt_disable_warnings_for_sources target)
    if(NOT TARGET ${target})
        return()
    endif()
    if(NOT ARGN)
        return()
    endif()
    set_source_files_properties(
        ${ARGN}
        TARGET_DIRECTORY ${target}
        PROPERTIES
            SKIP_CLANG_TIDY ON
    )
    foreach(_nt_source IN LISTS ARGN)
        set_property(SOURCE ${_nt_source} TARGET_DIRECTORY ${target} APPEND PROPERTY COMPILE_OPTIONS
            "$<$<AND:$<COMPILE_LANGUAGE:C>,$<C_COMPILER_ID:MSVC>>:/w>"
            "$<$<AND:$<COMPILE_LANGUAGE:C>,$<NOT:$<C_COMPILER_ID:MSVC>>>:-w>"
        )
    endforeach()
endfunction()

# Subprojects
add_subdirectory(engine)

if(NT_ENABLE_WEBGPU)
    if(CMAKE_TARGET_PLATFORM STREQUAL "windows")
        set(WEBGPU_BACKEND "DAWN" CACHE STRING "WebGPU backend implementation" FORCE)
    elseif(CMAKE_TARGET_PLATFORM STREQUAL "wasm")
        set(WEBGPU_BACKEND "EMSCRIPTEN" CACHE STRING "WebGPU backend implementation" FORCE)
    endif()
    set(WEBGPU_BUILD_FROM_SOURCE OFF CACHE BOOL "Build WebGPU backend from source" FORCE)
    FetchContent_Declare(webgpu_distribution
        GIT_REPOSITORY https://github.com/eliemichel/WebGPU-distribution.git
        GIT_TAG ${NT_WEBGPU_DISTRIBUTION_TAG}
        FIND_PACKAGE_ARGS
    )
    FetchContent_MakeAvailable(webgpu_distribution)
else()
    message(STATUS "WebGPU integration disabled (set NT_ENABLE_WEBGPU=ON to fetch Dawn on Windows).")
endif()

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
