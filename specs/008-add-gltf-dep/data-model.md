# Data Model — GLFW FetchContent Wiring

There is no persistent runtime data introduced by this feature. The only relevant concept is the FetchContent registration inside the sandbox build system.

## Entity: `glfw_target_registration`
- **Purpose**: Declares the upstream GLFW sources via `FetchContent_Declare` and makes the target available to consumer executables.
- **Fields**:
  - `URL`: `https://github.com/glfw/glfw/archive/refs/tags/3.4.0.tar.gz`
  - `Options`: `GLFW_BUILD_EXAMPLES/TESTS/DOCS OFF`, `GLFW_INCLUDE_NONE ON`
  - `Consumer Targets`: `sandbox_app` (others may opt-in later)
- **Lifecycle**: Declared once per configure; FetchContent downloads sources on demand and reuses the populated tree in subsequent builds.
- **Failure Modes**: Network failure halts configure with FetchContent’s error; developers rerun after restoring connectivity.
