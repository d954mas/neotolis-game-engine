cmake_minimum_required(VERSION 3.27)

project(nt_engine
    VERSION 0.1.0
    LANGUAGES C
)

if(CMAKE_C_COMPILER_ID STREQUAL "MSVC"
   OR (CMAKE_C_COMPILER_ID STREQUAL "Clang" AND CMAKE_C_SIMULATE_ID STREQUAL "MSVC"))
    set(CMAKE_C_STANDARD 17)
else()
    set(CMAKE_C_STANDARD 23)
endif()
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

add_subdirectory(engine)
add_subdirectory(testbeds/sandbox)
add_subdirectory(tests)
