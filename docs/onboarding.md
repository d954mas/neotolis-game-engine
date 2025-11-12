# Speckit Engine Onboarding

This guide summarizes the core steps required to configure and validate the bootstrap build system.

## 1. Install Toolchains

Follow the [requirements checklist](./requirements.md) to install:

- Emscripten SDK 4.0.x (4.0.19 recommended)
- LLVM/clang 17 (including `clang-cl` on Windows)
- CMake 3.27+

## 2. Clone and Configure Presets

```bash
git clone https://github.com/<org>/nt_engine.git
cd nt_engine
cmake --preset web-debug
cmake --build --preset web-debug
```

For Windows builds, run the configure/build commands from a Developer PowerShell prompt:

```pwsh
cmake --preset win-debug
cmake --build --preset win-debug
```

## 3. Validate Tests and Reports

```bash
ctest --preset web-debug
```

Ensure the following artifacts are emitted:

- `build/<preset>/tests/unit` — lifecycle smoke test binaries
- `build/<preset>/tests/microbench` — stub performance metrics
- `build/<preset>/tests/size` — size-report outputs

## 4. Explore the Sandbox

Run the sandbox executable to confirm lifecycle wiring:

```bash
# WebAssembly (served via emrun)
emrun --no_browser build/web-debug/sandbox/nt_sandbox.html

# Windows
build/win-debug/sandbox/nt_sandbox.exe
```

## 5. Next Steps

- Duplicate `engine/features/sample` to spin up a new feature module.
- Update `testbeds/sandbox/CMakeLists.txt` with the new module sources using `target_sources`.
- Add size-report and microbench coverage for the module as described in `docs/ci-guidelines.md`.

## 6. Documentation Review

Before merging documentation updates, request a peer review to confirm instructions remain accurate across Windows and WebAssembly environments. Capture feedback in the pull request description.
