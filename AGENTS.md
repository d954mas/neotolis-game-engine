# nt_engine Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-22

## Active Technologies

- C23 (clang-cl 17 on Windows, emcc/Clang 3.1.x for WebAssembly) + CMake ≥3.27, Emscripten SDK toolchain, LLVM/clang-cl 17, GLFW + WebGPU/WebGL2 stubs (placeholders only), cglm header-only math utilities (001-init-cmake-structure)

## Project Structure

```text
CMakeLists.txt
cmake/
├── toolchains/
└── presets/
engine/
├── core/
├── platform/{web,win}/
├── features/sample/
└── third_party/cglm/
testbeds/sandbox/
tests/{unit,microbench,size}/
ci/workflows/
```

## Commands

- Configure: `cmake --preset web-debug` / `cmake --preset win-debug`
- Build: `cmake --build --preset <preset-name>`
- Test: `ctest --preset <preset-name> --output-on-failure`

## Code Style

C23 (clang-cl 17 on Windows, emcc/Clang 3.1.x for WebAssembly): Follow standard conventions

## Recent Changes

- 001-init-cmake-structure: Added C23 (clang-cl 17 on Windows, emcc/Clang 3.1.x for WebAssembly) + CMake ≥3.27, Emscripten SDK toolchain, LLVM/clang-cl 17, GLFW + WebGPU/WebGL2 stubs (placeholders only), cglm header-only math utilities

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
