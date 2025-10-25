function(nt_configure_packaged_output)
    set(options)
    set(oneValueArgs TARGET APP_NAME)
    cmake_parse_arguments(NT_PACKAGE "${options}" "${oneValueArgs}" "" ${ARGN})

    if(NOT NT_PACKAGE_TARGET)
        message(FATAL_ERROR "nt_configure_packaged_output: TARGET argument is required")
    endif()

    if(NOT TARGET ${NT_PACKAGE_TARGET})
        message(FATAL_ERROR "nt_configure_packaged_output: TARGET '${NT_PACKAGE_TARGET}' does not exist")
    endif()

    if(NOT NT_PACKAGE_APP_NAME)
        message(FATAL_ERROR "nt_configure_packaged_output: APP_NAME argument is required")
    endif()

    if(NOT DEFINED NT_OUTPUT_ROOT OR "${NT_OUTPUT_ROOT}" STREQUAL "")
        message(FATAL_ERROR "nt_configure_packaged_output: NT_OUTPUT_ROOT must be defined before configuring artifacts")
    endif()

    if(NOT DEFINED CMAKE_BUILD_TYPE OR "${CMAKE_BUILD_TYPE}" STREQUAL "")
        message(FATAL_ERROR "nt_configure_packaged_output: CMAKE_BUILD_TYPE must be defined")
    endif()

    if(NOT DEFINED CMAKE_TARGET_PLATFORM OR "${CMAKE_TARGET_PLATFORM}" STREQUAL "")
        message(FATAL_ERROR "nt_configure_packaged_output: CMAKE_TARGET_PLATFORM must be defined")
    endif()

    string(TOLOWER "${CMAKE_BUILD_TYPE}" _nt_package_variant)
    string(TOLOWER "${CMAKE_TARGET_PLATFORM}" _nt_platform_folder)
    set(_nt_binary_dir "${NT_OUTPUT_ROOT}/${NT_PACKAGE_APP_NAME}/${_nt_platform_folder}/${_nt_package_variant}")
    set(_nt_target "${NT_PACKAGE_TARGET}")

    get_target_property(_nt_output_name ${_nt_target} OUTPUT_NAME)
    if(NOT _nt_output_name)
        set(_nt_output_name ${_nt_target})
    endif()

    add_custom_command(TARGET ${_nt_target} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove_directory "${_nt_binary_dir}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${_nt_binary_dir}"
        COMMENT "Refreshing ${_nt_binary_dir} for packaged artifacts"
    )

    if(CMAKE_TARGET_PLATFORM STREQUAL "windows")
        set(_nt_windows_binary "${_nt_binary_dir}/engine.exe")
        add_custom_command(TARGET ${_nt_target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:${_nt_target}>"
                "${_nt_windows_binary}"
            COMMENT "Packaging Windows executable for ${_nt_target} -> ${_nt_windows_binary}"
        )
    elseif(CMAKE_TARGET_PLATFORM STREQUAL "wasm")
        set(_nt_wasm_file "$<TARGET_FILE_DIR:${_nt_target}>/${_nt_output_name}.wasm")
        set(_nt_wasm_map "$<TARGET_FILE_DIR:${_nt_target}>/${_nt_output_name}.wasm.map")
        if(NOT DEFINED NT_WASM_EMIT_SOURCE_MAPS)
            message(FATAL_ERROR "nt_configure_packaged_output: NT_WASM_EMIT_SOURCE_MAPS not defined for wasm target; ensure the wasm toolchain sets it")
        endif()
        add_custom_command(TARGET ${_nt_target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:${_nt_target}>"
                "${_nt_binary_dir}/index.html"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_nt_wasm_file}"
                "${_nt_binary_dir}/engine.wasm"
            COMMENT "Packaging WebAssembly bundle for ${_nt_target}"
        )
        if(NT_WASM_EMIT_SOURCE_MAPS)
            add_custom_command(TARGET ${_nt_target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_nt_wasm_map}"
                    "${_nt_binary_dir}/engine.wasm.map"
                COMMENT "Copying WebAssembly source map for ${_nt_target}"
            )
        endif()
    else()
        message(FATAL_ERROR "nt_configure_packaged_output: Unsupported CMAKE_TARGET_PLATFORM='${CMAKE_TARGET_PLATFORM}'")
    endif()

    set_property(TARGET ${_nt_target} PROPERTY NT_ARTIFACT_BINARY_DIR "${_nt_binary_dir}")
endfunction()
