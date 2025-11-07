if(NOT NT_ENGINE_SOURCES)
    message(FATAL_ERROR "NT_ENGINE_SOURCES missing for microbench stub")
endif()

add_executable(test_microbench_stub
    test_frame_timing.c
)

target_sources(test_microbench_stub PRIVATE ${NT_ENGINE_SOURCES})

target_include_directories(test_microbench_stub
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

if(DEFINED NT_FAILFAST_ENFORCEMENT_TARGET AND TARGET ${NT_FAILFAST_ENFORCEMENT_TARGET})
    target_link_libraries(test_microbench_stub PRIVATE ${NT_FAILFAST_ENFORCEMENT_TARGET})
endif()
if(DEFINED NT_THIRD_PARTY_HEADERS_TARGET AND TARGET ${NT_THIRD_PARTY_HEADERS_TARGET})
    target_link_libraries(test_microbench_stub PRIVATE ${NT_THIRD_PARTY_HEADERS_TARGET})
endif()
add_test(NAME US3_microbench_stub COMMAND test_microbench_stub)

add_executable(qa_failfast_policy_microbench
    failfast_policy_stub.c
)

target_sources(qa_failfast_policy_microbench PRIVATE ${NT_ENGINE_SOURCES})
target_include_directories(qa_failfast_policy_microbench
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

if(DEFINED NT_FAILFAST_ENFORCEMENT_TARGET AND TARGET ${NT_FAILFAST_ENFORCEMENT_TARGET})
    target_link_libraries(qa_failfast_policy_microbench PRIVATE ${NT_FAILFAST_ENFORCEMENT_TARGET})
endif()
if(DEFINED NT_THIRD_PARTY_HEADERS_TARGET AND TARGET ${NT_THIRD_PARTY_HEADERS_TARGET})
    target_link_libraries(qa_failfast_policy_microbench PRIVATE ${NT_THIRD_PARTY_HEADERS_TARGET})
endif()
add_test(NAME qa_failfast_policy_microbench COMMAND qa_failfast_policy_microbench)
set_tests_properties(qa_failfast_policy_microbench PROPERTIES LABELS "failfast")
