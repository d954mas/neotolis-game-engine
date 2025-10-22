set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR wasm32)

set(EMSDK_PATH "$ENV{EMSDK}")
if(NOT EMSDK_PATH)
    message(FATAL_ERROR "EMSDK environment variable not set. Run 'source emsdk_env.sh' before configuring.")
endif()

set(EMSCRIPTEN_ROOT "${EMSDK_PATH}/upstream/emscripten" CACHE PATH "Path to Emscripten root")
if(NOT EXISTS "${EMSCRIPTEN_ROOT}/emcc")
    message(FATAL_ERROR "Emscripten toolchain not found at ${EMSCRIPTEN_ROOT}. Ensure EMSDK is installed and activated.")
endif()

set(CMAKE_C_COMPILER "${EMSCRIPTEN_ROOT}/emcc")
set(CMAKE_CXX_COMPILER "${EMSCRIPTEN_ROOT}/em++")

set(CMAKE_C_FLAGS_INIT "-Oz -flto -sSTRICT=1" )
set(CMAKE_EXE_LINKER_FLAGS_INIT "-sERROR_ON_UNDEFINED_SYMBOLS=1 -sASSERTIONS=1")

set(CMAKE_FIND_ROOT_PATH "${EMSCRIPTEN_ROOT}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/sandbox")
