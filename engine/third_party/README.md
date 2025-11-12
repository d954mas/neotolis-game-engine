# Third-Party Dependencies

This directory documents the third-party components referenced by CMake. FetchContent handles downloads on demand; no archives need to be checked in.

## GLFW 3.4.0

- **Upstream repo**: https://github.com/glfw/glfw
- **Tag**: `3.4.0`
- **Pin location**: `testbeds/sandbox/CMakeLists.txt`
- **Notes**: FetchContent downloads the archive automatically when configuring `web-*` or `win-*` presets. Update the URL/tag when bumping versions and rerun configure to fetch the new release.
