function(nt_add_size_report)
    set(options)
    set(oneValueArgs TARGET OUTPUT_DIR REPORT_NAME TARGET_NAME COMMENT REPORT_VAR PUBLISH_DIR PUBLISH_NAME)
    cmake_parse_arguments(NT_SIZE "${options}" "${oneValueArgs}" "" ${ARGN})

    if(NOT NT_SIZE_TARGET)
        message(FATAL_ERROR "nt_add_size_report: TARGET argument is required")
    endif()

    if(NOT TARGET ${NT_SIZE_TARGET})
        message(FATAL_ERROR "nt_add_size_report: TARGET '${NT_SIZE_TARGET}' does not exist")
    endif()

    if(NOT NT_SIZE_OUTPUT_DIR)
        set(NT_SIZE_OUTPUT_DIR "${CMAKE_BINARY_DIR}/tests/size")
    endif()

    if(NOT NT_SIZE_REPORT_NAME)
        set(NT_SIZE_REPORT_NAME "size-report.txt")
    endif()

    if(NOT NT_SIZE_TARGET_NAME)
        set(NT_SIZE_TARGET_NAME "${NT_SIZE_TARGET}_size_report")
    endif()

    if(NOT NT_SIZE_COMMENT)
        set(NT_SIZE_COMMENT "Generating size report for ${NT_SIZE_TARGET}")
    endif()

    set(_nt_report_path "${NT_SIZE_OUTPUT_DIR}/${NT_SIZE_REPORT_NAME}")

    set(_nt_publish_commands)
    if(NT_SIZE_PUBLISH_DIR)
        if(NOT NT_SIZE_PUBLISH_NAME)
            set(NT_SIZE_PUBLISH_NAME ${NT_SIZE_REPORT_NAME})
        endif()
        list(APPEND _nt_publish_commands
            COMMAND ${CMAKE_COMMAND} -E make_directory ${NT_SIZE_PUBLISH_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${_nt_report_path} ${NT_SIZE_PUBLISH_DIR}/${NT_SIZE_PUBLISH_NAME}
        )
    endif()

    add_custom_command(
        OUTPUT ${_nt_report_path}
        COMMAND ${CMAKE_COMMAND} -E make_directory ${NT_SIZE_OUTPUT_DIR}
        COMMAND ${CMAKE_SOURCE_DIR}/scripts/size_report.sh ${CMAKE_BINARY_DIR} ${NT_SIZE_OUTPUT_DIR}
        ${_nt_publish_commands}
        DEPENDS ${NT_SIZE_TARGET}
        COMMENT "${NT_SIZE_COMMENT}"
        VERBATIM
    )

    add_custom_target(${NT_SIZE_TARGET_NAME}
        DEPENDS ${_nt_report_path}
    )

    if(NT_SIZE_REPORT_VAR)
        set(${NT_SIZE_REPORT_VAR} ${_nt_report_path} PARENT_SCOPE)
    endif()
endfunction()
