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

add_test(NAME US3_microbench_stub COMMAND test_microbench_stub)
