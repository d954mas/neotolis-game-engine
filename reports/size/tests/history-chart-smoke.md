# History Chart Smoke Checklist

## Environment Prep

- [ ] Start a local server from `reports/size/` (e.g., `python -m http.server 8000`).
- [ ] Open `http://localhost:8000/report.html` in Chromium and Firefox.
- [ ] Validate the active folder has at least one `index.json` with ≥30 commits; regenerate reports if necessary.

## User Story 1 – Present historical growth

- [ ] Confirm the “Size History” section appears directly beneath the trend chart.
- [ ] Verify the line chart renders in chronological order and updates after selecting a different folder.
- [ ] Trigger a new report (or edit `index.json`) and reload the page to ensure the latest commit appears within ±1 % of the manifest totals.
- [ ] Review the console log for `[history-chart: render complete]` with sample count and duration.

## User Story 2 – Inspect commit context

- [ ] Click a history button to ensure the tooltip lists size (KB/MB), commit hash, localized timestamp, and commit message without changing selection on hover.
- [ ] Verify HEAD and MASTER commits show labeled badges in the button rail.
- [ ] Use the mouse wheel (or trackpad vertical scroll) to move horizontally across the commit buttons, and drag the button rail with the pointer to pan; confirm interactions feel smooth and buttons remain clickable.
- [ ] Use <kbd>Tab</kbd> to focus the first commit button, then <kbd>Arrow</kbd> keys / <kbd>Home</kbd> / <kbd>End</kbd> to navigate the history list; press <kbd>Enter</kbd> / <kbd>Space</kbd> to activate a selection and confirm the chart highlights the commit only after activation.
- [ ] Run an accessibility checker (axe or Lighthouse) to verify focus rings and ARIA labels meet WCAG AA expectations.

## User Story 3 – Segment review windows

- [ ] Click 30/90/180 commit buttons and check the chart updates with the correct number of samples.
- [ ] Reload the page and confirm the last selected window persists for the session.
- [ ] Open a new tab during the same session; confirm the stored window mode applies automatically.
- [ ] Inspect the console for `history-chart: render complete` and truncation/missing-commit warnings to confirm instrumentation remains active.

## Edge Cases & Messaging

- [ ] Switch to a folder with fewer than five commits and confirm the “More history needed” banner appears while still plotting available points.
- [ ] Temporarily remove artifacts from a commit and verify the chart still renders, logs the gap warning, and updates the message text.
- [ ] (Optional) Fabricate >180 commits to confirm the chart truncates to the latest 180 and displays the truncation message.
