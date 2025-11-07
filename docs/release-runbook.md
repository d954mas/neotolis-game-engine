# Release Runbook — Web Portal

## Portal Verification Checklist

1. Confirm `sandbox-size` workflow completed and `publish-web-portal` workflow succeeded (check the GitHub Actions UI).
2. Download the latest Pages artifact from the `publish-web-portal` run and spot-check the manifest (`manifest.json`) for the expected commit SHA.
3. Visit the deployed URL and `/tmp/portal-preview/index.html` (if built locally) on desktop and ≤768 px viewports; ensure both sandbox and report links return HTTP 200.
4. Review the footer freshness timestamp and compare against the latest `main` commit time (≤10 minutes difference).
5. Execute the manual smoke checklists:
   - `tests/size/manual/portal_access.md`
   - `tests/size/manual/portal_metrics.md`
6. Capture screenshots of the hero, sandbox card, and metrics card for archival in the release ticket.

## Troubleshooting Portal Deployment

- **Artifact mismatch**: Inspect `portal-deploy-manifest.json` from the workflow artifacts to confirm SHA256 values. Re-run `scripts/build-portal-preview.sh --ci` locally with the same artifact inputs to reproduce.
- **Workflow failure before deploy**: Re-run `publish-web-portal` with `workflow_run` inputs once `sandbox-size` succeeds. Check `scripts/build-portal-preview.sh` logs for gzip budget failures.
- **Broken links**: Use `npx --prefix web/portal broken-link-checker https://<org>.github.io/<repo>/ --ordered --recursive` to replicate CI checks and identify the failing path.
- **Stale timestamp**: Verify `scripts/portal/prepare-portal.js` receives the correct `--generated-at` and `--deployment-runtime` flags. Rebuild if the manifest timestamp predates the latest `main` commit.

## Stakeholder Feedback Template (SC-004)

- **Release window**: `<YYYY-MM-DD>`
- **Reviewer**: `<Name / Team>`
- **Sandbox experience (1–5)**: `<rating>` — Notes: `<observations>`
- **Build metrics clarity (1–5)**: `<rating>` — Notes: `<observations>`
- **Action items / follow-ups**: `<list of requested adjustments>`
