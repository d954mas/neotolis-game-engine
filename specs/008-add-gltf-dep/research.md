# Phase 0 Research — GLFW FetchContent Wiring

## Decision 1: Use FetchContent with upstream GitHub tag
- **Rationale**: FetchContent already ships with CMake and can download GLFW 3.4.0 directly from GitHub on every configure, removing the need for custom cache scripts or local mirrors. This keeps the workflow simple and matches the project goal of “just add the dependency”.
- **Alternatives considered**:
  - **Manual archive caching**: Adds maintenance overhead (scripts, checksums) without providing clear value for this feature.
  - **Git submodule**: Requires extra clone steps and increases repo size.
  - **System packages**: Not portable to WebAssembly.

## Decision 2: Link upstream target directly
- **Rationale**: Exposing the FetchContent-provided `glfw` target through `target_link_libraries(<target> PRIVATE glfw)` is the most direct path for consumers and avoids writing an engine wrapper.
- **Alternatives considered**:
  - **Custom `nt_glfw_*` wrapper**: Adds maintenance cost with no functional benefit for dependency wiring.
  - **Header-only forks**: Would diverge from upstream and complicate updates.

## Decision 3: Optional smoke flag instead of permanent runtime usage
- **Rationale**: A compile-time flag (`NT_SANDBOX_ENABLE_GLFW_SMOKE`) lets developers verify linkage via `glfwInit/glfwTerminate` when needed without shipping a permanent dependency in the sandbox.
- **Alternatives considered**:
  - **Always run the smoke check**: Unnecessary work for every developer and introduces startup costs.
  - **CI automation**: Out of scope per specification; manual smoke suffices.

## Best Practices Notes

1. Always disable `GLFW_BUILD_EXAMPLES/TESTS/DOCS` and enable `GLFW_INCLUDE_NONE` to keep binary size within the 20 KB budget.
2. Re-run configure after bumping the GLFW tag so FetchContent downloads the new release automatically.
3. Only enable the smoke definition locally when verifying linkage; leave it off in shared presets to avoid unnecessary work.
