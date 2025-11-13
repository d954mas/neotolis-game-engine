set(_NT_ENGINE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/core/nt_engine.c
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/web/nt_platform_web.c
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/win/nt_platform_win.c
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/web/nt_wasm_noexcept_stub.c
    ${CMAKE_CURRENT_SOURCE_DIR}/features/sample/nt_feature_sample.c
    ${CMAKE_CURRENT_SOURCE_DIR}/render/render.c
)

set(_NT_ENGINE_HEADERS
    ${CMAKE_CURRENT_SOURCE_DIR}/core/nt_engine.h
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/web/nt_platform_web.h
    ${CMAKE_CURRENT_SOURCE_DIR}/platform/win/nt_platform_win.h
    ${CMAKE_CURRENT_SOURCE_DIR}/features/sample/nt_feature_sample.h
    ${CMAKE_CURRENT_SOURCE_DIR}/render/glfw3webgpu.h
    ${CMAKE_CURRENT_SOURCE_DIR}/render/render.h
)

set(NT_ENGINE_SOURCES ${_NT_ENGINE_SOURCES} PARENT_SCOPE)
set(NT_ENGINE_HEADERS ${_NT_ENGINE_HEADERS} PARENT_SCOPE)

# Treat the GLFW WebGPU shim as third-party glue so we do not fail builds on its warnings.
set(_NT_ENGINE_VENDOR_SHIMS)
set(NT_ENGINE_VENDOR_SHIMS ${_NT_ENGINE_VENDOR_SHIMS} PARENT_SCOPE)
set(NT_GLFW3WEBGPU_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/render/glfw3webgpu.c" PARENT_SCOPE)

option(NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS "Treat vendor includes as SYSTEM headers" ON)

add_library(nt_third_party_headers INTERFACE)
set(_NT_THIRDPARTY_CGLM "${CMAKE_CURRENT_SOURCE_DIR}/third_party/cglm")
if(NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS)
    target_include_directories(nt_third_party_headers SYSTEM INTERFACE ${_NT_THIRDPARTY_CGLM})
else()
    target_include_directories(nt_third_party_headers INTERFACE ${_NT_THIRDPARTY_CGLM})
endif()

set(NT_THIRD_PARTY_HEADERS_TARGET nt_third_party_headers PARENT_SCOPE)
