project(nt_sandbox LANGUAGES C)

option(NT_SANDBOX_ENABLE_SIZE_REPORT "Generate size report for the sandbox target" OFF)

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
