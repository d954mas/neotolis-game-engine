# Feature Module Scaffolding Checklist

Follow these steps to add a new engine feature module using the bootstrap structure.

1. **Duplicate the sample module**
   - Copy `engine/features/sample` to `engine/features/<module-name>`.
   - Rename both `.c` and `.h` files to `nt_feature_<module-name>.c/h`.
2. **Wire headers**
   - Update the new header to export `nt_feature_<module-name>_init` and related APIs.
   - Record memory model expectations (arena vs none) in comments.
3. **Embed sources**
   - Add the new source file to `testbeds/sandbox/CMakeLists.txt` using `target_sources`.
   - If the module has platform-specific hooks, add them to the respective `engine/platform/<target>/` directories.
4. **Update tests**
   - Add a compilation smoke test under `tests/unit/` that links the new module.
   - Update CTest to include the test with the appropriate label (e.g., `USX_feature_<module>`).
5. **Regenerate size & microbench reports**
   - Run `ctest --preset web-debug` and `ctest --preset win-debug`.
   - Capture the new size-report baseline and annotate expected deltas.

This checklist ensures contributors can onboard within a single user story and keeps the engine embedded directly within consuming testbeds.
