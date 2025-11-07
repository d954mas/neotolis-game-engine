# Implementation Plan: Publish Web Demo & Reports Portal

**Branch**: `005-publish-web-report` | **Date**: 2025-11-06 | **Spec**: specs/005-publish-web-report/spec.md
**Input**: Feature specification from `/specs/005-publish-web-report/spec.md`

## Summary

Standing up a public-facing portal hosted on GitHub Pages that links to the latest sandbox build and engine size report. The plan wires the existing `testbeds/sandbox` WebAssembly artifact and `reports/size` output into a dedicated publishing workflow that runs after `update-size-reports`, verifies checksums, stages both the sandbox bundle and full dashboards, and refreshes a responsive `index.html` landing page with freshness metadata and descriptive error states for missing artifacts.

## Technical Context

**Language/Version**: HTML5, CSS3, ES2020 (vanilla) for portal assets; GitHub Actions YAML v1 for CI authoring; C/CMake toolchains untouched.  
**Frameworks & Tooling**: Static HTML/CSS + minimal JS for interactivity; `actions/deploy-pages`, `actions/upload-artifact`, `actions/download-artifact`, Lighthouse CLI (bundle diagnostics mode) for performance smoke.  
**Artifact Sources**: `testbeds/sandbox` WebAssembly bundle (CI artifact), `reports/size` dashboard (generated via `update-size-reports`).  
**Hosting Target**: GitHub Pages served from `gh-pages` branch; content produced by CI job.  
**Testing Strategy**:  
- Automated: GitHub Actions job sequence, artifact integrity checks (SHA256), link-checker CLI, Lighthouse smoke in CI.  
- Manual: Spot-check portal freshness timestamp, sandbox launch, and report load post-deploy.  
**Performance Goals**: Landing page FCP ≤3 s on 25 Mbps (tracked via Lighthouse), sandbox load path unchanged from existing artifact budget.  
**Constraints & Budgets**: Static portal bundle ≤150 KB gzip (FR-008); sandbox `.wasm` bundle (HTML/JS/wasm) ≤200 KB gzip to preserve the 3 s load budget without runtime measurement; no new runtime allocations or engine code changes; Pages deploy gated on successful `update-size-reports`.  
**Integration Touchpoints**: GitHub Actions workflow updates, portal asset staging directory (`web/portal`), documentation (README, release notes).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Binary Budget Supremacy**: No engine binaries change; portal bundle capped at 150 KB gzip with automated size guard in CI before publishing.
- [x] **Deterministic Memory Discipline**: Feature ships static assets only; runtime allocations stay within existing sandbox/report boundaries and no new allocators are introduced.
- [x] **Performance-Oriented Portability**: Workflow preserves current microbench + size-report pipeline order and adds Lighthouse smoke to guard portal performance across web/desktop reviewers.
- [x] **Spec-Led Delivery**: Approved spec `specs/005-publish-web-report/spec.md` defines requirements, instrumentation, and budgets; this plan references it directly.
- [x] **Embedded Feature Isolation**: Engine code remains embedded in testbeds; portal work stays in CI and static assets without breaking embedded-source model.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
web/
└── portal/
    ├── index.html            # CI-generated landing page template (includes metrics card + failure messaging)
    ├── styles.css            # Shared styling for portal tiles + footer
    ├── scripts/
    │   └── freshness.js      # Injects timestamp, handles missing-artifact messaging
    ├── sandbox/              # Staged sandbox bundle (HTML/JS/wasm) copied from CI artifacts
    └── assets/               # Placeholder for static icons (≤10 KB total)

reports/size/                # Existing dashboard artifacts (consumed, not modified)
testbeds/sandbox/            # Source for WebAssembly build artifact (consumed)

.github/workflows/
├── update-size-reports.yml          # existing job, referenced for dependency & artifact publication
└── publish-web-portal.yml           # new workflow chaining sandbox build + artifact validation + Pages deploy with SLA logging

web/portal/reports/size/             # staged copy of latest size dashboard (produced by workflow)

docs/
└── release-runbook.md        # Add “Verify portal updated” checklist entry
```

**Structure Decision**: Add a dedicated `web/portal` directory for static site assets governed by CI, extend GitHub Actions workflows to stage artifacts, and update documentation. No engine headers/sources move; sandbox and size-report producers remain authoritative artifact sources.

## Complexity Tracking

No constitutional violations identified; complexity tracking not required.
