add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/tests/size/size-report.txt
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/tests/size
    COMMAND ${CMAKE_SOURCE_DIR}/scripts/size_report.sh ${CMAKE_BINARY_DIR} ${CMAKE_BINARY_DIR}/tests/size
    DEPENDS nt_sandbox
    COMMENT "Generating size report"
)

add_custom_target(size_report ALL DEPENDS ${CMAKE_BINARY_DIR}/tests/size/size-report.txt)

add_test(NAME US3_size_report
    COMMAND ${CMAKE_COMMAND} -E cat ${CMAKE_BINARY_DIR}/tests/size/size-report.txt
)
