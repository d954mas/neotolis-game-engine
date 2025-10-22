# nt_engine

Bootstrap repository for the Speckit engine. This branch seeds the project structure, toolchain presets, sandbox testbed, and CI workflows.

## Build Presets

```bash
cmake --preset web-debug
cmake --build --preset web-debug
ctest --preset web-debug
```

See `docs/onboarding.md` for additional details, including Windows commands and troubleshooting notes.

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
