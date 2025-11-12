<!--
Sync Impact Report
Version change: 3.0.0 → 3.1.0
Modified principles:
- II. Deterministic Memory Discipline (explicit bans on STL/streams, upfront load allocation, clarified ownership)
- V. Embedded Feature Isolation → V. Embedded Minimal Surface
Added sections:
- None
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
Follow-up TODOs:
- None
-->

# Speckit Constitution

## Core Principles

### I. Binary Budget Supremacy
- All release builds for Windows and WebAssembly MUST use clang-based toolchains with `-Oz` and link-time optimization enabled.
- Every merge request MUST project `.wasm` and native binary deltas; increases above 2% require a mitigation plan approved before merge.
- Each feature MUST keep its compiled contribution within the 30 KB code budget while helping the overall engine remain under 200 KB for WebAssembly targets.

This principle keeps Speckit instantly loadable on bandwidth-constrained devices and preserves our primary competitive differentiator.

### II. Deterministic Memory Discipline
- All runtime allocations MUST route through the `nt_alloc_*` interface so that allocators can be swapped and audited centrally.
- Features MUST preallocate memory via fixed-size arenas or arrays; dynamic resizing (`realloc`, implicit container growth) is forbidden.
- Resource loading paths MUST reserve required memory up front (e.g., when parsing collection files); steady-state frame loops may not allocate.
- Standard library facilities that hide heap usage (`std::string`, `std::vector`, `<iostream>`, `<stringstream>`, smart pointers, etc.) are prohibited; custom structs or arena-backed helpers MUST express ownership explicitly.
- Total runtime memory consumption MUST stay within the 32 MB budget per application; waivers demand explicit instrumentation and rollback plans.

Deterministic memory usage ensures predictable behavior across WebAssembly sandboxes and constrained desktop testbeds.

### III. Performance-Oriented Portability
- Hot-path code MUST be benchmarked through the web and Windows microbench targets before release toggles ship.
- Build configurations MUST preserve parity between debug and release workflows, and CI MUST track the microbench and size-report targets on every change.
- Performance optimizations MUST not compromise binary size or memory budgets; any trade-offs require documented rationale in the accompanying spec.

This principle guarantees that Speckit stays fast across both primary platforms without regressing our tight resource constraints.

### IV. Spec-Led Delivery
- Every initiative begins with an approved specification capturing the C API surface, memory model, binary and RAM impact, and the CMake snippet that embeds engine sources into the target testbed.
- Plan outputs MUST map directly to the specification, and no implementation work may merge without the spec, plan, and tasks explicitly linked.
- Specifications MUST enumerate required instrumentation, CI checks, and acceptance criteria before any code is written.

Spec-first delivery prevents accidental scope creep and keeps resource budgets enforceable before implementation starts.

### V. Embedded Minimal Surface
- The engine ships as source embedded directly into consuming testbeds; producing standalone library artifacts is prohibited.
- Headers and sources MUST live side by side per feature module, exposing only `nt_`-prefixed public entry points.
- External dependencies MUST be header-only or single-file libraries with no hidden allocations, and every dependency is gated behind an explicit feature flag.
- Apply the rule “If we don’t need it, we don’t use it”: features require documented user demand, minimal scope, and removal of dead code as soon as it loses a consumer.

Maintaining embedded, isolated features preserves portability and minimal footprint across build targets.

## Platform & Build Constraints

- Primary target: WebAssembly through Emscripten (Clang); secondary target: Windows builds via clang-cl for rapid iteration.
- Graphics stack: WebGPU with a WebGL2 fallback; Windows builds integrate GLFW with OpenGL for windowing and input.
- Supported build modes: `debug` and `release`, with release builds enforcing `-Oz` and LTO; CI profiles include `web-debug`, `web-release`, `win-debug`, and `win-release`.
- Engine sources remain feature-oriented and embedded: each consuming game or test defines its own `CMakeLists.txt` enumerating required features and source files.
- Math utilities rely on the embedded, header-only `cglm` package, enabled on demand.

## Quality Gates & Runtime Guardrails

- Logging uses a compile-time `NT_LOG_LEVEL`; debug builds may adjust verbosity at runtime via `nt_log_set_level()`, while release builds strip logging overhead.
- CI runs CTest suites plus microbench and size-report targets; merges fail if `.wasm` text/data sections regress by more than 2% without an approved mitigation plan.
- Instrumentation tasks MUST cover binary size, memory usage, and performance metrics; validation steps belong in specs and tasks before implementation starts.
- Error handling relies on status codes or structs; assertions are restricted to debug builds, and the public API consistently uses the `nt_` prefix.
- Any third-party addition MUST document memory and size impact, provide knobs to disable unused functionality, and satisfy Principle V’s isolation rules.
- Defensive programming that merely repeats earlier validation (e.g., redundant pointer checks, setting structs to zero before immediately assigning fields) is banned; ensure assets, build tooling, or spec tasks catch invalid data earlier in the pipeline.

## Governance

- This constitution supersedes prior process docs; teams MUST cite relevant clauses within plans, specs, and task lists before work begins.
- Amendments require a written RFC referencing impacted principles, an updated Sync Impact Report, and synchronized updates to dependent templates before merge.
- Semantic versioning applies: MAJOR for removed or rewritten principles, MINOR for new principles or major guidance, PATCH for clarifications.
- Compliance reviews: each PR links CI artifacts for size, memory, and performance; releases are blocked until constitutional gates pass or receive documented waivers.
- Steering cadence: conduct constitution reviews at least quarterly and ahead of any platform expansion to validate budgets and governance health.

**Version**: 3.1.0 | **Ratified**: 2025-10-22 | **Last Amended**: 2025-11-12
