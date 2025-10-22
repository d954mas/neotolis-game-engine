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
