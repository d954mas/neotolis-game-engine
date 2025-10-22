set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

find_program(CLANG_CL_EXECUTABLE clang-cl HINTS "$ENV{LLVM_HOME}/bin")
if(NOT CLANG_CL_EXECUTABLE)
    message(FATAL_ERROR "clang-cl not found. Install LLVM 17 and set LLVM_HOME or ensure clang-cl is on PATH.")
endif()

set(CMAKE_C_COMPILER "${CLANG_CL_EXECUTABLE}")
set(CMAKE_C_FLAGS_INIT "/std:c23 /Zi /W4 /WX")

if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_C_FLAGS_RELEASE "/O2 /GL /Gw /DNDEBUG")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "/LTCG /OPT:REF /OPT:ICF")
else()
    set(CMAKE_C_FLAGS_DEBUG "/Od /RTC1 /MDd /fsanitize=address")
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/sandbox")
