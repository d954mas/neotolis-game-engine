# Speckit Bootstrap Prerequisites

The Project Structure & CMake Bootstrap feature depends on the following toolchain versions. Install them before configuring any build presets.

## Toolchains

- **Emscripten SDK 3.1.x** (tested with 3.1.57) — provides the WebAssembly toolchain used by the `web-*` presets.
- **LLVM/Clang 17** (`clang-cl` on Windows) — used for native Windows builds through the `win-*` presets.
- **CMake 3.27 or newer** — required for preset support and multi-platform configuration management.
- **Ninja** (optional) — recommended generator for both platforms when using single-config builds.

## Environment Setup

1. Install Emscripten per the official instructions:
   ```bash
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   ./emsdk install 3.1.57
   ./emsdk activate 3.1.57
   source ./emsdk_env.sh
   ```
2. Install LLVM/Clang 17:
   - Windows: via LLVM installer or Visual Studio components including clang-cl.
   - macOS/Linux: package manager (`brew install llvm@17`, `apt install clang-17`, etc.).
3. Ensure `cmake --version` reports 3.27 or newer.

## Validation

After installation, verify the environment by running:

```bash
cmake --version
clang --version
emcc --version
```

All commands should complete successfully before running `cmake --preset <preset>`.
