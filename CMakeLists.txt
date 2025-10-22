cmake_minimum_required(VERSION 3.27)

project(nt_engine
    VERSION 0.1.0
    LANGUAGES C
)

# Common language settings
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Tooling
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Print active build type (handy when using Presets)
message(STATUS "Configuring ${CMAKE_PROJECT_NAME} in ${CMAKE_BUILD_TYPE} mode")

# Subprojects
add_subdirectory(engine)
add_subdirectory(testbeds/sandbox)
add_subdirectory(tests)
