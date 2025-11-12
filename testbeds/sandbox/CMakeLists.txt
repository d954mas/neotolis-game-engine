project(nt_sandbox LANGUAGES C)

include(FetchContent)

option(NT_SANDBOX_ENABLE_SIZE_REPORT "Generate size report for the sandbox target" OFF)
option(NT_SANDBOX_ENABLE_GLFW_SMOKE "Run a glfwInit/glfwTerminate smoke test" OFF)

set(_nt_sandbox_use_emscripten_glfw OFF)
if(CMAKE_SYSTEM_NAME STREQUAL "Emscripten")
    set(_nt_sandbox_use_emscripten_glfw ON)
endif()

FetchContent_Declare(glfw
    URL https://github.com/glfw/glfw/releases/download/3.4/glfw-3.4.zip
    DOWNLOAD_EXTRACT_TIMESTAMP OFF
)
message(STATUS "Fetching GLFW 3.4.0 via FetchContent (network required)")

# Keep GLFW lean for our embedded use-case
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_INCLUDE_NONE ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(glfw)

# Disable clang-tidy for the third-party target so upstream style warnings don't fail our build
# keep clang-tidy off this third-party target
set(_nt_glfw_system_includes)
if(TARGET glfw)
    set_target_properties(glfw PROPERTIES
        C_CLANG_TIDY ""
        COMPILE_WARNING_AS_ERROR OFF
    )
    if(CMAKE_C_COMPILER_ID MATCHES "Clang")
        target_compile_options(glfw PRIVATE -w)
    endif()
    get_target_property(_nt_glfw_system_includes glfw INTERFACE_INCLUDE_DIRECTORIES)
    if(CMAKE_SYSTEM_NAME STREQUAL "Emscripten")
        target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=199309L)
    endif()
endif()
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
if(_nt_glfw_system_includes AND NOT _nt_glfw_system_includes MATCHES "NOTFOUND")
    target_include_directories(nt_sandbox SYSTEM PRIVATE ${_nt_glfw_system_includes})
endif()

if(DEFINED NT_FAILFAST_ENFORCEMENT_TARGET AND TARGET ${NT_FAILFAST_ENFORCEMENT_TARGET})
    target_link_libraries(nt_sandbox PRIVATE ${NT_FAILFAST_ENFORCEMENT_TARGET})
endif()

if(DEFINED NT_THIRD_PARTY_HEADERS_TARGET AND TARGET ${NT_THIRD_PARTY_HEADERS_TARGET})
    target_link_libraries(nt_sandbox PRIVATE ${NT_THIRD_PARTY_HEADERS_TARGET})
endif()


if(_nt_sandbox_use_emscripten_glfw)
    set_target_properties(nt_sandbox PROPERTIES LINKER_LANGUAGE CXX)
    # Trim the contrib.glfw3 port by disabling joystick polling and multi-window support.
    target_link_options(nt_sandbox PUBLIC
        "--use-port=contrib.glfw3:disableJoystick=true:disableMultiWindow=true")
    # WebGL/HTML5 glue provides the emscripten_webgl_* symbols required by the GLFW port
    target_link_libraries(nt_sandbox PRIVATE html5 GL)
else()
    target_link_libraries(nt_sandbox PRIVATE glfw)
endif()

# Export packaged artifacts for downstream consumers
nt_configure_packaged_output(
    TARGET nt_sandbox
    APP_NAME sandbox
)

if(NT_SANDBOX_ENABLE_SIZE_REPORT)
    include(${CMAKE_SOURCE_DIR}/cmake/NTSizeReport.cmake)

    get_target_property(_nt_sandbox_artifacts nt_sandbox NT_ARTIFACT_BINARY_DIR)
    if(NOT _nt_sandbox_artifacts)
        message(WARNING "nt_sandbox does not expose NT_ARTIFACT_BINARY_DIR; size report will not be copied to packaged output")
    endif()

    set(_nt_size_publish_args)
    if(_nt_sandbox_artifacts)
        list(APPEND _nt_size_publish_args
            PUBLISH_DIR ${_nt_sandbox_artifacts}
            PUBLISH_NAME size-report.txt
        )
    endif()

    nt_add_size_report(
        TARGET nt_sandbox
        TARGET_NAME nt_sandbox_size_report
        OUTPUT_DIR ${CMAKE_BINARY_DIR}/tests/size
        REPORT_NAME size-report.txt
        COMMENT "Generating sandbox size report"
        ${_nt_size_publish_args}
    )
endif()
