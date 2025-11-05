set(NT_SANDBOX_SIZE_REPORT ${CMAKE_BINARY_DIR}/tests/size/size-report.txt)

if(TARGET nt_sandbox_size_report)
    add_custom_target(size_report
        DEPENDS nt_sandbox_size_report
    )

    add_test(NAME US3_size_report
        COMMAND ${CMAKE_COMMAND} -E cat ${NT_SANDBOX_SIZE_REPORT}
    )
else()
    message(STATUS "Sandbox size report target is disabled. Enable it with -DNT_SANDBOX_ENABLE_SIZE_REPORT=ON.")
endif()
