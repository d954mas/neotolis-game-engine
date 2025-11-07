include(CTest)

if(NT_FAILFAST_WARNING_FLAGS)
    add_test(NAME failfast_warning_gate
        COMMAND ${CMAKE_COMMAND}
            -DSOURCE_FILE=${CMAKE_SOURCE_DIR}/tests/fixtures/warning_violation.c
            -DCOMPILER=${CMAKE_C_COMPILER}
            -DWARNING_FLAGS="${NT_FAILFAST_WARNING_FLAGS}"
            -DBUILD_DIR=${CMAKE_BINARY_DIR}/warning-gate
            -P ${CMAKE_SOURCE_DIR}/tests/ci/test_warning_gate.cmake
    )
    set_tests_properties(failfast_warning_gate PROPERTIES LABELS "failfast")
endif()

add_subdirectory(unit)
add_subdirectory(microbench)
add_subdirectory(size)
