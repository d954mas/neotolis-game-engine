# Zero-Warning Policy & Third-Party Isolation

The fail-fast initiative enables `/Wall /WX` (clang-cl) and `-Wall -Wextra -Wpedantic -Werror` (Emscripten) across every preset. To prevent vendor headers from breaking the build, `engine/CMakeLists.txt` exposes the `NT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS` option (ON by default) which injects third-party include paths (e.g., `engine/third_party/cglm`) as `SYSTEM` headers via the `nt_third_party_headers` interface target.

## How to use

1. Link any target that consumes vendor headers against the interface:
   ```cmake
   target_link_libraries(my_target PRIVATE nt_third_party_headers)
   ```
2. If you need to debug warning output from a vendor directory, configure with `-DNT_FAILFAST_SUPPRESS_THIRDPARTY_WARNINGS=OFF`; headers will be included normally so you can inspect compiler output.
3. When adding a new third-party dependency, update `engine/CMakeLists.txt` with the additional include path (still under the same interface target) and mention the component in this document.

This keeps the zero-warning gate strict for engine/testbed code while isolating unavoidable noise from external code.
