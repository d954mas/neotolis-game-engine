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

# Subprojects
add_subdirectory(engine)
add_subdirectory(testbeds/sandbox)
add_subdirectory(tests)
