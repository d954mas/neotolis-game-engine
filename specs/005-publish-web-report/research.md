# Phase 0 Research — Publish Web Demo & Reports Portal

## Decision: Deployment mechanism (GitHub Actions → GitHub Pages via `gh-pages`)
- **Rationale**: GitHub Pages supports static hosting with built-in actions (`actions/deploy-pages`) that publish artifacts from CI, aligning with the requirement to trigger deployment only after `update-size-reports`.
- **Alternatives considered**:  
  - Self-hosted S3 bucket: rejected because it introduces new infrastructure and credentials.  
  - GitHub Releases assets: rejected because release cadence is slower than per-commit `main` updates.

## Decision: Artifact integrity validation (SHA256 checksum + manifest metadata)
- **Rationale**: Calculating SHA256 hashes for sandbox bundle and `reports/size` archive before copying into the portal ensures FR-006 compliance and blocks stale/missing artifacts (`FR-007`), while keeping tooling simple (`shasum` / `powershell Get-FileHash`).
- **Alternatives considered**:  
  - Size-only checks: rejected because they can miss corruption or partial uploads.  
  - External signing service: rejected due to complexity and lack of immediate need.

## Decision: Handling missing or stale artifacts (fail-fast CI + portal fallback messaging)
- **Rationale**: CI should stop deployment when required artifacts are absent or older than the triggering commit, but the portal still needs clear messaging if an outage occurs; embedding freshness timestamp and conditional cards covers both requirements.
- **Alternatives considered**:  
  - Silent deployment with broken links: rejected, violates FR-007 and degrades trust.  
  - Manual approval gates: rejected for slowing automated publishing without adding detection value.
