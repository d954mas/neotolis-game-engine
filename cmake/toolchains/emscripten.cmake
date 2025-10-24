# emscripten.cmake

set(CMAKE_SYSTEM_NAME Emscripten)
set(CMAKE_SYSTEM_PROCESSOR wasm32)

set(EMSDK_PATH "$ENV{EMSDK}")
if(NOT EMSDK_PATH)
    message(FATAL_ERROR "EMSDK env var is not set. Activate emsdk (emsdk_env) before configuring.")
endif()

set(EMSCRIPTEN_ROOT "${EMSDK_PATH}/upstream/emscripten" CACHE PATH "Path to Emscripten root")

if(WIN32)
    set(_EMCC_PATH "${EMSCRIPTEN_ROOT}/emcc.bat")
    set(_EMXX_PATH "${EMSCRIPTEN_ROOT}/em++.bat")
else()
    set(_EMCC_PATH "${EMSCRIPTEN_ROOT}/emcc")
    set(_EMXX_PATH "${EMSCRIPTEN_ROOT}/em++")
endif()

if(NOT EXISTS "${_EMCC_PATH}")
    message(FATAL_ERROR "emcc not found at ${_EMCC_PATH}")
endif()
if(NOT EXISTS "${_EMXX_PATH}")
    message(FATAL_ERROR "em++ not found at ${_EMXX_PATH}")
endif()

set(CMAKE_C_COMPILER   "${_EMCC_PATH}")
set(CMAKE_CXX_COMPILER "${_EMXX_PATH}")
set(CMAKE_FIND_ROOT_PATH "${EMSCRIPTEN_ROOT}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)


set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/sandbox")

set(WEB_SOURCE_MAP_BASE "" CACHE STRING "Source-map base URL, e.g. http://localhost:8000/")


set(CMAKE_C_FLAGS_DEBUG              "-O0 -g" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_DEBUG            "-O0 -g" CACHE STRING "" FORCE)
set(CMAKE_EXE_LINKER_FLAGS_DEBUG     "-g -gsource-map -sASSERTIONS=2 -sSAFE_HEAP=1 -sSTACK_OVERFLOW_CHECK=2 -sDEMANGLE_SUPPORT=1 --profiling-funcs" CACHE STRING "" FORCE)


if(WEB_SOURCE_MAP_BASE)
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS_DEBUG} --source-map-base=${WEB_SOURCE_MAP_BASE}")
endif()


set(CMAKE_C_FLAGS_RELEASE            "-Oz -flto" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE          "-Oz -flto" CACHE STRING "" FORCE)
set(CMAKE_EXE_LINKER_FLAGS_RELEASE   "-sASSERTIONS=0 -sERROR_ON_UNDEFINED_SYMBOLS=1 -sSTRICT=1" CACHE STRING "" FORCE)
