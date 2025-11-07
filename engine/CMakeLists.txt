set(NT_ENGINE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/core/nt_engine.c
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/web/nt_platform_web.c
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/win/nt_platform_win.c
    ${CMAKE_CURRENT_SOURCE_DIR}/features/sample/nt_feature_sample.c
    PARENT_SCOPE
)

set(NT_ENGINE_HEADERS
    ${CMAKE_CURRENT_SOURCE_DIR}/core/nt_engine.h
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/web/nt_platform_web.h
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/win/nt_platform_win.h
    ${CMAKE_CURRENT_SOURCE_DIR}/features/sample/nt_feature_sample.h
    PARENT_SCOPE
)

option(NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS "Treat vendor includes as SYSTEM headers" ON)

add_library(nt_third_party_headers INTERFACE)
set(_NT_THIRDPARTY_CGLM "${CMAKE_CURRENT_SOURCE_DIR}/third_party/cglm")
if(NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS)
    target_include_directories(nt_third_party_headers SYSTEM INTERFACE ${_NT_THIRDPARTY_CGLM})
else()
    target_include_directories(nt_third_party_headers INTERFACE ${_NT_THIRDPARTY_CGLM})
endif()

set(NT_THIRD_PARTY_HEADERS_TARGET nt_third_party_headers PARENT_SCOPE)
