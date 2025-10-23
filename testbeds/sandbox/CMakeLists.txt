project(nt_sandbox LANGUAGES C)

add_executable(nt_sandbox
    main.c
)

# Embed engine sources directly into the sandbox executable
if(NOT NT_ENGINE_SOURCES)
    message(FATAL_ERROR "NT_ENGINE_SOURCES not defined. Ensure engine CMakeLists.txt exported source list.")
endif()

target_sources(nt_sandbox
    PRIVATE
        ${NT_ENGINE_SOURCES}
)

target_include_directories(nt_sandbox
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

# Use consistent compile flags for size-sensitive builds
if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    target_compile_options(nt_sandbox PRIVATE -Wall -Wextra -Werror)
else()
    target_compile_options(nt_sandbox PRIVATE /W4 /WX)
endif()
