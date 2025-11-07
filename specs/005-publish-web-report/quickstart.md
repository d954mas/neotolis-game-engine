# Quickstart — Publish Web Demo & Reports Portal

1. **Prepare local environment**
   - Ensure `node` ≥18 (for link checking and Lighthouse CLI) and `python3` ≥3.8 (existing size tooling).
   - Install portal tooling: `npm install --global lighthouse @githubnext/github-pages-deploy-action` (or add to CI cache step).

2. **Run size and sandbox generators locally (optional validation)**
   - `cmake --preset web-release && cmake --build --preset web-release` to produce the sandbox wasm bundle under `testbeds/sandbox/out`.
   - `python reports/size/update.py --input <sandbox-output> --output reports/size/local-preview` to generate a local report snapshot.

3. **Assemble portal preview**
   - From repo root run `scripts/build-portal-preview.sh --sandbox testbeds/sandbox/out --report reports/size` (script added in implementation).
   - Inspect `/tmp/portal-preview/index.html` ensuring links resolve and freshness timestamp matches the latest commit.

4. **Exercise CI pipeline end-to-end**
   - Push to a branch; GitHub Actions should run `update-size-reports` → `build-sandbox` → `publish-web-portal`.
   - Verify `publish-web-portal` job uploads the Pages artifact and prints SHA256 checksums for sandbox and report bundles.

5. **Smoke test deployed site**
   - Hit `https://<org>.github.io/<repo>/` once deployment finishes; confirm landing page timestamp, sandbox link, and report link all return HTTP 200.
   - Run `npx broken-link-checker https://<org>.github.io/<repo>/` to ensure no broken links.

6. **Monitor budgets**
   - Review job logs for gzip size summaries (portal bundle ≤150 KB, sandbox bundle ≤200 KB) and deployment elapsed time relative to `update-size-reports`.
   - If thresholds fail, investigate artifact sizes or regressions before approving the PR.
