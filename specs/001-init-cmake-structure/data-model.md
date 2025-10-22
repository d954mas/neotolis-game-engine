# Data Model — Project Structure & CMake Bootstrap

## BuildProfile

- **Description**: Named configuration representing a concrete toolchain and optimization combo used by developers and CI.
- **Attributes**:
  - `name` (string, required, unique among profiles) — e.g., `web-debug`, `win-release`.
  - `platform` (enum: `web`, `windows`) — determines toolchain file selection.
  - `optimization` (enum: `debug`, `release`) — toggles flags such as `-Oz`, LTO, assertions.
  - `ci_workflow` (string, required) — identifier of the CI job that must execute the profile.
  - `artifact_dir` (path) — relative path where build outputs are emitted per preset.
- **Relationships**:
  - One `BuildProfile` references many `EngineModule` sources through CMake `target_sources`.
  - Each `BuildProfile` must register with at least one CTest target (`size_report`, `microbench_stub`).
- **Lifecycle**:
  - Created during repository bootstrap with baseline presets.
  - Extended when new platforms or build modes are introduced.
  - Deprecated when governance retires a platform; removal requires CI update and preset deletion.

## EngineModule

- **Description**: Feature-scoped pairing of `.c` and `.h` files plus optional platform-specific variants embedded into consuming targets.
- **Attributes**:
  - `module_name` (string, required, unique) — canonical identifier (e.g., `sample`).
  - `public_header` (path, required) — exported API location (`engine/features/sample/nt_feature_sample.h`).
  - `source_file` (path, required) — implementation location.
  - `feature_flag` (string, optional) — compile-time toggle gating inclusion.
  - `estimated_size_kb` (float) — budget impact tracked by size-report target.
  - `allocations` (enum: `none`, `arena`, `fixed_buffer`) — indicates memory pattern; bootstrap defaults to `none`.
- **Relationships**:
  - Each `EngineModule` is embedded by one or more `BuildProfile` targets.
  - Platform-specific shims (`engine/platform/web`, `engine/platform/win`) map to modules through dedicated headers.
- **Lifecycle**:
  - Created as part of scaffold to illustrate feature isolation.
  - Expanded when real functionality is implemented; removal requires update to sandbox and CI.
  - Metrics updated via size and microbench reports after each build.

## ToolchainConfig (Supporting Concept)

- **Description**: Aggregates compiler, linker, and flag settings consumed by presets.
- **Attributes**:
  - `toolchain_file` (path, required) — e.g., `cmake/toolchains/emscripten.cmake`.
  - `compiler_id` (string) — `Clang`, `emcc`, etc.
  - `min_version` (string) — minimum supported compiler version.
  - `lto_enabled` (boolean) — defaults to `true` for release builds.
  - `sanitizers` (set) — debug sanitizers toggled per preset.
- **Relationships**:
  - Each `BuildProfile` references one `ToolchainConfig`.
- **Lifecycle**:
  - Maintained alongside presets; updated when compiler upgrades occur.
