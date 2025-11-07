# Manual Verification Checklist — Portal Access

## Scenario: Desktop Portal Smoke Test

1. Run the full CI pipeline or `scripts/build-portal-preview.sh` locally to stage the portal.
2. Open the deployed URL (or `/tmp/portal-preview/index.html`) in a desktop browser.
3. Confirm the hero section renders the portal title, description, and two primary call-to-action buttons.
4. Click “Try the Sandbox” and ensure the sandbox loads without HTTP errors.
5. Click “Engine Build Report” and confirm `report.html` renders with charts and tables.
6. Inspect the footer timestamp; it must match the current commit window (≤10 minutes old).
7. Review the console for JavaScript errors — the page must load without failures.

## Scenario: Mobile Viewport Smoke Test (≤768 px)

1. With the portal loaded, open the browser’s responsive design tools or resize the window to ≤768 px.
2. Ensure cards stack vertically with appropriate padding and typography remains legible.
3. Tap each CTA button to confirm they remain reachable and trigger navigation to sandbox/report pages.
4. Verify status text wraps without overlapping card borders.
5. Collapse/expand devtools to ensure layout remains stable after rotation/resizing.

## Scenario: Manifest Failover

1. Temporarily rename `manifest.json` to simulate a missing file and reload the portal.
2. Confirm both cards show “Unavailable” states with descriptive status messages.
3. Restore the manifest and reload to verify the cards recover automatically.
4. Record any anomalies before reverting test changes.
