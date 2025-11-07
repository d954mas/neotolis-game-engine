if(NOT DEFINED SOURCE_FILE)
  message(FATAL_ERROR "SOURCE_FILE not provided")
endif()
if(NOT DEFINED COMPILER)
  message(FATAL_ERROR "COMPILER not provided")
endif()
if(NOT DEFINED WARNING_FLAGS)
  message(FATAL_ERROR "WARNING_FLAGS not provided")
endif()
if(NOT DEFINED BUILD_DIR)
  set(BUILD_DIR "${CMAKE_BINARY_DIR}/warning-gate")
endif()

file(MAKE_DIRECTORY "${BUILD_DIR}")
set(OUTPUT_FILE "${BUILD_DIR}/warning_violation.o")

set(_flags)
foreach(flag ${WARNING_FLAGS})
  if(NOT flag STREQUAL "")
    list(APPEND _flags ${flag})
  endif()
endforeach()

set(cmd ${COMPILER} ${_flags} -c "${SOURCE_FILE}" -o "${OUTPUT_FILE}")
execute_process(
  COMMAND ${cmd}
  RESULT_VARIABLE compile_result
  OUTPUT_VARIABLE compile_out
  ERROR_VARIABLE compile_err
)

if(compile_result EQUAL 0)
  message(FATAL_ERROR "Expected warning gate to fail compilation, but command succeeded.\nCommand: ${cmd}\nStdout:${compile_out}\nStderr:${compile_err}")
endif()

message(STATUS "Warning gate failed compilation as expected (exit code ${compile_result}).")
