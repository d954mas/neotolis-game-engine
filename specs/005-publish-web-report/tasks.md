# Tasks: Publish Web Demo & Reports Portal

**Input**: Design documents from `/specs/005-publish-web-report/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Define failing link-check or Lighthouse smoke verification before marking each story complete; automation steps are embedded in the GitHub Actions workflow tasks.

**Instrumentation**: Ensure checksum verification, deployment logging, and performance metrics are captured in CI before closing user stories.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Budgets**: Enforce the 150 KB gzip portal bundle limit and existing `.wasm` budgets via CI checks prior to deployment.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish baseline portal structure and repository placeholders

- [X] T001 Create portal scaffold (`web/portal/index.html`, `web/portal/styles.css`, `web/portal/scripts/freshness.js`) with minimal placeholder content
- [X] T002 Add asset placeholders (`web/portal/assets/.gitkeep`) and update `.gitignore` to exclude portal build artifacts (`web/portal/dist/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared tooling required before any user story implementation

**⚠️ CRITICAL**: Complete this phase before working on any user story

- [X] T003 Implement artifact preparation script `scripts/portal/prepare-portal.js` to download sandbox/report artifacts, compute SHA256 hashes, stage `web/portal/sandbox/` and `web/portal/reports/size/`, and emit `web/portal/manifest.json`
- [X] T004 Create portal preview wrapper `scripts/build-portal-preview.sh` that invokes the preparation script and stages output to `/tmp/portal-preview`
- [X] T005 Define portal tooling package manifest `web/portal/package.json` with checksum utilities and Lighthouse CLI as dev dependencies

**Checkpoint**: Artifact staging pipeline ready — user stories can begin

---

## Phase 3: User Story 1 - Access Latest Web Demo (Priority: P1) 🎯 MVP

**Goal**: Deliver a responsive landing page with working links to sandbox and build report for web stakeholders.

**Independent Test**: Open the deployed portal on desktop and ≤768 px viewport, ensuring sandbox and report links return HTTP 200 and render without layout issues.

### Implementation

- [X] T006 [US1] Build hero layout and link cards in `web/portal/index.html` referencing manifest placeholders for sandbox/report URLs
- [X] T007 [P] [US1] Implement responsive styling (grid, mobile breakpoints, button states) in `web/portal/styles.css`
- [X] T008 [P] [US1] Wire basic DOM bootstrap in `web/portal/scripts/freshness.js` to load `manifest.json`, toggle unavailable states, and inject the deployment timestamp
- [X] T009 [US1] Copy the latest sandbox bundle (HTML/JS/wasm) into `web/portal/sandbox/` during the preview build so the “Try the Sandbox” link resolves without direct artifact downloads
- [X] T010 [US1] Copy the latest `reports/size` dashboard bundle into `web/portal/reports/size/` during the preview build so report links resolve without direct artifact downloads
- [X] T011 [US1] Capture manual smoke checklist for portal links in `tests/size/manual/portal_access.md`

**Checkpoint**: Landing page functional and independently verifiable

---

## Phase 4: User Story 2 - Automated Publishing After Size Reports (Priority: P2)

**Goal**: Ensure GitHub Pages deployment only occurs when sandbox and update-size-reports succeed with verified artifacts.

**Independent Test**: Trigger the CI pipeline; confirm `publish-web-portal.yml` runs after `update-size-reports`, halts on checksum mismatch, and deploys only when artifacts are valid.

### Implementation

- [X] T012 [US2] Author `.github/workflows/publish-web-portal.yml` with `workflow_run` dependency on `update-size-reports` and sandbox build jobs
- [X] T013 [US2] Add steps in `publish-web-portal.yml` to download artifacts, run `scripts/portal/prepare-portal.js`, assert SHA256 checksums, and upload the GitHub Pages artifact
- [X] T014 [P] [US2] Extend `scripts/build-portal-preview.sh` with CI flags (artifact paths, commit SHA) and gzip size verification (portal bundle ≤150 KB, sandbox bundle ≤200 KB) before packaging `web/portal/dist/`
- [X] T015 [US2] Emit descriptive failure annotations and job-summary diagnostics when artifacts are missing, stale, or checksum validation fails in `publish-web-portal.yml`
- [X] T016 [US2] Log the elapsed time between `update-size-reports` completion and portal deployment in `publish-web-portal.yml`, failing if the 10-minute SLA is exceeded

**Checkpoint**: Automated publishing gated by artifact validation and CI sequencing

---

## Phase 5: User Story 3 - Review Build Metrics Snapshot (Priority: P3)

**Goal**: Surface key binary size and performance metrics on the portal, sourced from the latest size report.

**Independent Test**: After a successful deployment, verify the portal displays commit hash, build timestamp, wasm delta, and microbench metrics matching `reports/size/report.html`.

### Implementation

- [X] T017 [US3] Parse `reports/size/index.json` within `web/portal/scripts/freshness.js` to derive build metrics (commit hash, wasm delta KB, microbench ms)
- [X] T018 [P] [US3] Render metrics summary card in `web/portal/index.html` with graceful degradation when data is missing
- [X] T019 [US3] Add Lighthouse CI step in `.github/workflows/publish-web-portal.yml` to report bundle sizes and portal performance metrics (no additional runtime measurement) in the workflow summary
- [X] T020 [US3] Generate portal metrics validation checklist `tests/size/manual/portal_metrics.md`

**Checkpoint**: Build metrics visible and validated without overriding previous stories

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, observability, and quality assurance

- [X] T021 Update `docs/release-runbook.md` with “Verify portal updated” checklist and troubleshooting steps
- [X] T022 [P] Add broken-link checker step to `.github/workflows/publish-web-portal.yml` using `npx broken-link-checker` post deploy
- [X] T023 [P] Export deployment manifest (checksums, timestamps) to GitHub Actions artifacts in `scripts/portal/prepare-portal.js` for auditing
- [X] T024 Capture stakeholder feedback template in `docs/release-runbook.md` (or `docs/portal-feedback.md`) to support SC-004 satisfaction tracking

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → Phase 2 → User Stories (Phases 3–5) → Phase 6**
- User stories begin only after Phase 2 completes

### User Story Order

1. **US1 (P1)** – Establish functional landing page (MVP)
2. **US2 (P2)** – Automate publishing and artifact validation
3. **US3 (P3)** – Surface build metrics and performance checks

### Parallel Opportunities

- US1 styling (T007) and script bootstrap (T008) can proceed in parallel once manifest loader exists.
- US2 workflow authoring (T012) can happen alongside preview script enhancements (T014) after foundational scripts are ready.
- US3 metrics rendering (T018) can run parallel with Lighthouse integration (T019) since they touch different files.

## Implementation Strategy

1. Stand up portal scaffolding and artifact preparation tooling (Phases 1–2).
2. Deliver the MVP landing page (US1) to satisfy primary stakeholder needs.
3. Layer in CI automation and gating (US2) to maintain data freshness.
4. Add build metrics presentation and performance checks (US3).
5. Finish with documentation, link checking, and audit trail polish (Phase 6).
