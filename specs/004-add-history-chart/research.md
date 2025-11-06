# Phase 0 Research — Size Report History Chart

## Decision: Sample window sizing (30/90/180 commits client-side capped at 180)
- **Rationale**: Matches spec requirement for adjustable review windows while keeping front-end arrays bounded (≤ 180 samples) and aligning with manifest-provided commit counts in `reports/size/sandbox/*/index.json`.
- **Alternatives considered**:  
  - Unlimited history: rejected due to unbounded browser memory and rendering cost.  
  - Fixed 90-commit window only: rejected because release engineers explicitly need short- and long-range comparisons.

## Decision: Tooltip accessibility pattern (click + keyboard activation with persistent panel)
- **Rationale**: Keeps selection stable (no hover dependency), supports keyboard activation, and mirrors existing dashboard layout by updating the dedicated tooltip panel below the chart.
- **Alternatives considered**:  
  - Hover-only tooltips: rejected for lack of keyboard support and accidental selection changes.  
  - Separate detail panel per point: adds layout complexity without added insight.

## Decision: Preference persistence scope (sessionStorage)
- **Rationale**: Reuses existing dashboard preference helper, satisfies "persist within session" requirement, and avoids cross-device state or backend changes.
- **Alternatives considered**:  
  - Local persistent storage: rejected to avoid new privacy considerations.  
  - No persistence: rejected because spec mandates session persistence.

## Decision: Instrumentation via console logging and performance marks
- **Rationale**: Performance marks provide measurable render timing while console logs report render completion, truncation, and missing commit gaps without requiring backend changes.
- **Alternatives considered**:  
  - Restoring telemetry counters: rejected due to lack of backend support.  
  - Omitting instrumentation: rejected because render timing must remain observable.
