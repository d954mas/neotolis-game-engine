# Research Log — Project Structure & CMake Bootstrap

## Toolchain & Build System

- **Decision**: Adopt CMake 3.27+ with platform-specific toolchain files for Emscripten and clang-cl.
- **Rationale**: CMake offers first-class preset support, integrates with both Emscripten and Visual Studio environments, and aligns with Speckit’s principle of embedding sources directly while keeping configuration declarative.
- **Alternatives considered**:
  - **Meson/Ninja**: Faster incremental builds but lacks widespread Windows IDE integration expected by contributors.
  - **Manual makefiles**: Lightweight, yet harder to maintain across Windows/Web and incompatible with preset-based developer experience.

## Preset & Profile Layout

- **Decision**: Provide four named presets (`web-debug`, `web-release`, `win-debug`, `win-release`) that map 1:1 with constitutional CI profiles.
- **Rationale**: Ensures parity between local developer builds and automated pipelines, and enables predictable artifact locations for size/microbench reporting.
- **Alternatives considered**:
  - **Single multi-config generator**: Simplifies setup but complicates Emscripten workflows where single-config ninja builds are typical.
  - **Ad-hoc command snippets**: Faster to draft but risk drift and onboarding friction.

## CI & Testing Hooks

- **Decision**: Seed CTest targets for size-report and microbench stubs alongside a lifecycle smoke test suite.
- **Rationale**: Aligns new repository with constitutional gates, providing immediate feedback on size/perf budgets even before real subsystems exist.
- **Alternatives considered**:
  - **Delay CI instrumentation**: Faster bootstrap yet violates governance by leaving budgets unenforced.
  - **External scripts**: More flexible but introduces duplication and maintenance overhead versus CTest integration.

## Directory & Module Structure

- **Decision**: Organize sources under `engine/core`, `engine/platform/{web,win}`, `engine/features/sample`, and embed via `testbeds/sandbox`.
- **Rationale**: Mirrors the spec’s embedded feature isolation principle, keeping `.c/.h` pairs co-located and simplifying future feature drops.
- **Alternatives considered**:
  - **Monolithic src directory**: Minimal but erodes modular clarity and complicates selective embedding.
  - **Per-platform repositories**: Overkill for bootstrap and conflicts with requirement to ship engine as embedded sources.

## Documentation & Quickstart

- **Decision**: Provide a quickstart covering toolchain installation, preset usage, and CI command sequence.
- **Rationale**: Reduces onboarding time to hit the SC-003 metric (≤1 setup question) and ensures reproducible builds.
- **Alternatives considered**:
  - **Rely solely on README**: Keeps docs shorter but risks divergence and incomplete onboarding coverage.
