add_executable(test_engine_lifecycle
    test_engine_lifecycle.c
)

if(NOT NT_ENGINE_SOURCES)
    message(FATAL_ERROR "NT_ENGINE_SOURCES missing for lifecycle test")
endif()

target_sources(test_engine_lifecycle PRIVATE ${NT_ENGINE_SOURCES})

target_include_directories(test_engine_lifecycle
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

add_test(NAME US1_engine_lifecycle COMMAND test_engine_lifecycle)

add_executable(test_feature_sample
    test_feature_sample.c
)

target_sources(test_feature_sample PRIVATE ${NT_ENGINE_SOURCES})

target_include_directories(test_feature_sample
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

add_test(NAME US2_feature_sample COMMAND test_feature_sample)
