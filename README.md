# nt_engine

Bootstrap repository for the Speckit engine. This branch seeds the project structure, toolchain presets, sandbox testbed, and CI workflows.

## Build Presets

```bash
cmake --preset web-debug
cmake --build --preset web-debug
ctest --preset web-debug
```

See `docs/onboarding.md` for additional details, including Windows commands and troubleshooting notes.

## Running Tests Separately

Tests are now opt-in so regular sandbox builds stay lean. Use the `*-tests` presets when you want to exercise them:

```bash
cmake --preset win-debug-tests     # or web-debug-tests, win-release-tests, etc.
cmake --build --preset win-debug-tests
ctest --preset win-debug-tests
```

Alternatively, add `-DNT_ENABLE_TESTS=ON` to any `cmake --preset ...` invocation if you want to temporarily include tests in an existing build tree.

## Sandbox Project Toggle

The sandbox testbed can also be enabled/disabled per build. It is on by default for the standard presets, but you can skip it when you only need the engine libraries (or enable it for a custom preset):

```bash
cmake --preset win-debug -DNT_PROJECT_SANDBOX=OFF   # engine-only build
cmake --preset win-debug -DNT_PROJECT_SANDBOX=ON    # explicitly include sandbox
```

Future projects can follow the same pattern by introducing their own `NT_PROJECT_*` options.

## Directory Overview

```
CMakeLists.txt
cmake/
engine/
testbeds/sandbox/
tests/
ci/workflows/
```

Refer to `docs/feature-modules.md` before adding new feature modules.
