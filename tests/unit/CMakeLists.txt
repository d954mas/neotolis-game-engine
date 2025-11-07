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

if(DEFINED NT_FAILFAST_ENFORCEMENT_TARGET AND TARGET ${NT_FAILFAST_ENFORCEMENT_TARGET})
    target_link_libraries(test_engine_lifecycle PRIVATE ${NT_FAILFAST_ENFORCEMENT_TARGET})
endif()
if(DEFINED NT_THIRD_PARTY_HEADERS_TARGET AND TARGET ${NT_THIRD_PARTY_HEADERS_TARGET})
    target_link_libraries(test_engine_lifecycle PRIVATE ${NT_THIRD_PARTY_HEADERS_TARGET})
endif()

add_test(NAME US1_engine_lifecycle COMMAND test_engine_lifecycle)

add_executable(test_feature_sample
    test_feature_sample.c
)

target_sources(test_feature_sample PRIVATE ${NT_ENGINE_SOURCES})

target_include_directories(test_feature_sample
    PRIVATE
        ${CMAKE_SOURCE_DIR}
)

if(DEFINED NT_FAILFAST_ENFORCEMENT_TARGET AND TARGET ${NT_FAILFAST_ENFORCEMENT_TARGET})
    target_link_libraries(test_feature_sample PRIVATE ${NT_FAILFAST_ENFORCEMENT_TARGET})
endif()
if(DEFINED NT_THIRD_PARTY_HEADERS_TARGET AND TARGET ${NT_THIRD_PARTY_HEADERS_TARGET})
    target_link_libraries(test_feature_sample PRIVATE ${NT_THIRD_PARTY_HEADERS_TARGET})
endif()

add_test(NAME US2_feature_sample COMMAND test_feature_sample)
