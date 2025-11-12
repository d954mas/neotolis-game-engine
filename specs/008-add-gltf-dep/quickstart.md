# Quickstart — GLFW FetchContent Wiring

Goal: configure and build the sandbox with GLFW downloaded automatically via FetchContent.

## 1. Configure presets (network required)
```bash
cmake --preset win-debug
# or
cmake --preset web-debug
```
CMake will download `glfw-3.4.0.tar.gz` during the first configure. Check the log for `GLFW download` to confirm the fetch succeeded.

## 2. Optional smoke check
```bash
cmake --preset win-debug -DNT_SANDBOX_ENABLE_GLFW_SMOKE=ON
cmake --build --preset win-debug --target sandbox_app
build/win-debug/sandbox_app.exe
```
When the flag is enabled the binary logs `GLFW smoke check passed` before running the normal engine lifecycle, proving that linkage works.

## 3. Monitor size locally
```bash
cmake --build --preset web-debug --target size-report
```
Ensure the delta stays within +20 KB. No CI jobs or new tests are added for this dependency-only change.

## 4. Version bumps
- Update the FetchContent declaration in `testbeds/sandbox/CMakeLists.txt` (URL + tag) and re-run configure to download the new release.
- Document the new tag in `engine/third_party/README.md` so downstream consumers know which version is pinned.
