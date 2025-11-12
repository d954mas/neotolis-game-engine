# Implementation Plan: GLFW FetchContent Wiring

**Branch**: `008-add-gltf-dep` | **Date**: 2025-11-12 | **Spec**: `/mnt/c/projects/nt_engine/specs/008-add-gltf-dep/spec.md`
**Input**: Feature specification from `/specs/008-add-gltf-dep/spec.md`

**Note**: This plan covers wiring GLFW via FetchContent only—no cache mirroring or wrapper APIs.

## Summary

Add FetchContent plumbing to download GLFW 3.4.0 directly from GitHub during configure, link it into `sandbox_app`, and document the optional smoke test so future features can link the upstream target without additional work.

## Technical Context

**Language/Version**: C23 across clang-cl 17 (Windows) and emcc/Clang 3.1.x (WebAssembly) with `-Oz`/LTO for release builds.  
**Primary Dependencies**: GLFW 3.4.0, cglm, internal `nt_alloc_*`.  
**Storage**: No persistent assets/caches.  
**Testing**: Manual configure/build + optional smoke run; no CI automation required.  
**Target Platform**: WebAssembly + Windows.  
**Project Type**: Embedded engine sources consumed via per-testbed CMake targets.  
**Performance Goals**: Keep binary delta ≤20 KB; optional smoke completes ≤2 s.  
**Constraints**: `.wasm` ≤200 KB, per-feature code ≤30 KB, deterministic logging.  
**Scale/Scope**: Touch `testbeds/sandbox/CMakeLists.txt`, root `CMakeLists.txt` (light), doc set (feature modules + quickstart).  
**Integration Notes**: FetchContent handles downloads; offline mode intentionally unsupported.

## Constitution Check

- [x] **Binary Budget Supremacy**: Spec enforces ≤20 KB growth with mitigation guidance.  
- [x] **Deterministic Memory Discipline**: No new persistent allocations; optional smoke uses stack locals only.  
- [x] **Performance-Oriented Portability**: Manual smoke must succeed on both presets within 2 s.  
- [x] **Spec-Led Delivery**: Spec defines scenarios, embedding snippet, and budgets.  
- [x] **Embedded Minimal Surface**: No new engine modules; GLFW is linked directly into sandbox via source embedding.

## Project Structure

```text
specs/008-add-gltf-dep/
├── spec.md
├── plan.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md

engine/
├── platform/{web,win}/
└── third_party/

testbeds/
└── sandbox/
    ├── CMakeLists.txt  # FetchContent wiring
    └── main.c          # optional smoke guard
```

**Structure Decision**: Only sandbox CMake + docs change; no new folders or cache directories are introduced.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _None_ | — | — |
