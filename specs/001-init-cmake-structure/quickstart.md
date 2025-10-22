# Quickstart — Project Structure & CMake Bootstrap

## 1. Install Prerequisites

1. Install **Emscripten SDK 3.1.x**  
   ```bash
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   ./emsdk install 3.1.57
   ./emsdk activate 3.1.57
   source ./emsdk_env.sh
   ```
2. Install **LLVM/Clang 17** with `clang-cl` (Windows) or via your package manager on macOS/Linux.
3. Install **CMake 3.27+** and ensure it is available on your PATH.
4. (Windows) Install **Ninja** or ensure Visual Studio 2022 is available for generator integration.

## 2. Clone the Repository

```bash
git clone https://github.com/<org>/nt_engine.git
cd nt_engine
git checkout 001-init-cmake-structure
```

## 3. Configure Presets

All commands run from the repository root.

```bash
# WebAssembly debug build
cmake --preset web-debug
cmake --build --preset web-debug

# Windows debug build (from Developer Command Prompt)
cmake --preset win-debug
cmake --build --preset win-debug
```

> Release variants (`web-release`, `win-release`) enable LTO and `-Oz` automatically.

## 4. Run Baseline Tests

```bash
# Execute lifecycle smoke tests, size report, and microbench stub
ctest --preset web-debug
ctest --preset win-debug
```

Inspect generated reports:

```bash
cat build/web-debug/tests/size/size-report.txt
ctest --preset web-debug -R US3_microbench_stub --output-on-failure
```

Artifacts and reports are emitted under `build/<preset>/`.

## 5. Explore Sandbox Testbed

```bash
# WebAssembly output (serves via emrun or custom host)
emrun --no_browser build/web-debug/sandbox/sandbox.html

# Windows executable
build/win-debug/sandbox/sandbox.exe
```

The sandbox prints lifecycle events confirming `nt_engine_init`, `nt_engine_frame`, and `nt_engine_shutdown` wiring.

## 6. Add New Engine Modules

1. Copy `engine/features/sample` to a new directory (e.g., `engine/features/sprites`).
2. Rename files to `nt_feature_sprites.c/h`.
3. Add the new files to `testbeds/sandbox/CMakeLists.txt` via `target_sources`.
4. Reconfigure using the desired preset and rebuild.

## 7. CI Integration

- GitHub Actions workflows are seeded under `ci/workflows/*.yml`.
- Each workflow invokes its matching preset and publishes size/microbench outputs.
- Update workflows if you add new presets or rename modules.

## 8. Troubleshooting

- Missing toolchains: rerun the EMSDK or LLVM setup steps and ensure environment variables are set before configuring presets.
- CMake cache issues: delete `build/<preset>` directories and rerun `cmake --preset ...`.
- Size-report regressions (>2%): review compiled sources and consider toggling optional diagnostics behind feature flags before merging.

> Request a teammate to follow this quickstart before declaring the feature complete. Integrate their feedback into `docs/onboarding.md` or this document.
