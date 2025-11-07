(function(){
if (typeof window === 'undefined') { return; }
if (window.historyChart) { return; }
const HISTORY_DEFAULT_WINDOW = '90';
const WINDOW_OPTIONS = ['30', '90', '180'];
const MAX_HISTORY_SAMPLES = 180;
const WINDOW_STORAGE_KEY = 'historyWindow';

function createEmptySeries() {
    return {
        samples: [],
        allSamples: [],
        windowMode: HISTORY_DEFAULT_WINDOW,
        minSizeBytes: 0,
        maxSizeBytes: 0,
        gaps: 0,
        truncated: false,
        missingSampleCount: 0,
    };
}

function toEpochMilliseconds(value) {
    if (!value) {
        return null;
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
        return null;
    }
    return parsed.getTime();
}

function formatSampleLabel(commit) {
    const sha = (commit.git_sha || 'UNKNOWN').slice(0, 7);
    const message =
        commit.git_message && commit.git_message !== 'UNKNOWN'
            ? commit.git_message
            : commit.subject || '';
    if (!message) {
        return sha;
    }
    return `${sha} — ${message}`;
}

function computeTotalSizeBytes(artifacts) {
    if (!Array.isArray(artifacts)) {
        return 0;
    }
    return artifacts.reduce((sum, artifact) => {
        const size = Number(artifact?.size_bytes ?? 0);
        return sum + (Number.isFinite(size) && size >= 0 ? size : 0);
    }, 0);
}

function normalizeWindowMode(value) {
    if (WINDOW_OPTIONS.includes(value)) {
        return value;
    }
    return HISTORY_DEFAULT_WINDOW;
}

function loadStoredWindowMode() {
    try {
        const stored = typeof sessionStorage !== 'undefined'
            ? sessionStorage.getItem(WINDOW_STORAGE_KEY)
            : null;
        return normalizeWindowMode(stored || HISTORY_DEFAULT_WINDOW);
    } catch (error) {
        console.warn('history-chart: unable to access sessionStorage', error);
        return HISTORY_DEFAULT_WINDOW;
    }
}

function persistWindowMode(mode) {
    try {
        if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem(WINDOW_STORAGE_KEY, normalizeWindowMode(mode));
        }
    } catch (error) {
        console.warn('history-chart: unable to persist window preference', error);
    }
}

function sliceSamplesForWindow(samples, windowMode) {
    const count = Number.parseInt(windowMode, 10);
    if (!Number.isFinite(count) || count <= 0) {
        return [...samples];
    }
    if (samples.length <= count) {
        return [...samples];
    }
    return samples.slice(samples.length - count);
}

function formatSizeKb(bytes) {
    if (!Number.isFinite(bytes)) {
        return '0 KB';
    }
    if (bytes >= 1024 * 1024) {
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
    return `${(bytes / 1024).toFixed(1)} KB`;
}

function updateHistoryTooltip(series, tooltipEl, sampleIndex) {
    if (!tooltipEl) {
        return;
    }
    if (!series?.samples?.length) {
        tooltipEl.hidden = true;
        tooltipEl.innerHTML = '';
        return;
    }
    const index =
        typeof sampleIndex === 'number' && sampleIndex >= 0
            ? Math.min(sampleIndex, series.samples.length - 1)
            : series.samples.length - 1;
    const sample = series.samples[index];
    if (!sample) {
        tooltipEl.hidden = true;
        tooltipEl.innerHTML = '';
        return;
    }
    const message = sample.metadata?.message || sample.label || '';
    tooltipEl.hidden = false;
    tooltipEl.innerHTML = `
        <strong>Commit:</strong> ${sample.metadata?.gitSha?.slice(0, 7) || 'UNKNOWN'}<br/>
        <strong>Size:</strong> ${formatSizeKb(sample.totalSizeBytes)}<br/>
        <strong>Date:</strong> ${new Date(sample.committedAtEpochMs).toLocaleString()}<br/>
        <strong>Message:</strong> ${message || '—'}
    `;
}

function describeSeries(series) {
    if (!series.samples.length) {
        return 'History chart unavailable: no samples to plot.';
    }
    const first = series.samples[0];
    const last = series.samples[series.samples.length - 1];
    const startDate = new Date(first.committedAtEpochMs).toLocaleString();
    const endDate = new Date(last.committedAtEpochMs).toLocaleString();
    const truncatedNote = series.truncated
        ? 'History truncated to the most recent 180 commits.'
        : '';
    return `History chart showing ${series.samples.length} commits. Oldest sample ${startDate}, newest sample ${endDate}. Size range ${formatSizeKb(series.minSizeBytes)} to ${formatSizeKb(series.maxSizeBytes)}. ${truncatedNote}`.trim();
}

function clampSamples(samples) {
    if (samples.length <= MAX_HISTORY_SAMPLES) {
        return { samples, truncated: false };
    }
    // Keep the most recent entries (samples sorted ascending by timestamp).
    const start = samples.length - MAX_HISTORY_SAMPLES;
    return { samples: samples.slice(start), truncated: true };
}

function calculateMinMax(samples) {
    if (!samples.length) {
        return { minSizeBytes: 0, maxSizeBytes: 0 };
    }
    let min = Number.POSITIVE_INFINITY;
    let max = Number.NEGATIVE_INFINITY;
    for (const sample of samples) {
        if (sample.totalSizeBytes < min) {
            min = sample.totalSizeBytes;
        }
        if (sample.totalSizeBytes > max) {
            max = sample.totalSizeBytes;
        }
    }
    return { minSizeBytes: min, maxSizeBytes: max };
}

function updateSeriesWindow(series, windowMode) {
    const normalizedMode = normalizeWindowMode(windowMode);
    const baseSamples = Array.isArray(series.allSamples)
        ? series.allSamples
        : series.samples;
    const visibleSamples = sliceSamplesForWindow(baseSamples, normalizedMode);
    const { minSizeBytes, maxSizeBytes } = calculateMinMax(visibleSamples);
    series.windowMode = normalizedMode;
    series.samples = visibleSamples;
    series.minSizeBytes = minSizeBytes;
    series.maxSizeBytes = maxSizeBytes;
    return series;
}

/**
 * Transform manifest data into chronologically sorted samples.
 * @param {object} manifest Root manifest loaded from reports/size/index.json
 * @param {object} folderIndex Folder-specific index manifest
 * @returns {object} History series data structure
 */
function hydrateHistorySeries(manifest, folderIndex) {
    void manifest;

    const commits = Array.isArray(folderIndex?.commits)
        ? [...folderIndex.commits]
        : [];
    const samples = [];
    let skippedInvalidTimestamp = 0;
    let missingArtifactsCount = 0;

    for (const commit of commits) {
        const committedAtEpochMs = toEpochMilliseconds(commit?.date);
        if (committedAtEpochMs === null) {
            skippedInvalidTimestamp += 1;
            continue;
        }

        const artifacts = Array.isArray(commit?.artifacts)
            ? commit.artifacts
            : [];
        const totalSizeBytes = computeTotalSizeBytes(artifacts);
        const missingArtifacts = artifacts.length === 0;
        if (missingArtifacts) {
            missingArtifactsCount += 1;
        }

        const commitId =
            commit?.id ||
            `${commit?.kind || 'commit'}:${commit?.git_sha || 'UNKNOWN'}`;

        samples.push({
            commitId,
            totalSizeBytes,
            committedAtEpochMs,
            label: formatSampleLabel(commit || {}),
            missingArtifacts,
            metadata: {
                gitSha: commit?.git_sha || 'UNKNOWN',
                date: commit?.date || null,
                message: commit?.git_message || commit?.subject || '',
                kind: commit?.kind || '',
                branch: commit?.branch || '',
            },
        });
    }

    samples.sort(
        (a, b) => a.committedAtEpochMs - b.committedAtEpochMs,
    );

    const originalLength = samples.length;
    const { samples: clampedSamples, truncated } = clampSamples(samples);

    if (skippedInvalidTimestamp > 0) {
        console.warn(
            'history-chart: skipped commits without valid timestamps',
            {
                folder: folderIndex?.folder || 'unknown',
                skippedInvalidTimestamp,
            },
        );
    }
    if (missingArtifactsCount > 0) {
        console.warn('history-chart: commits missing artifact data', {
            folder: folderIndex?.folder || 'unknown',
            missingArtifactsCount,
        });
    }
    if (truncated) {
        console.info('history-chart: truncated history to most recent commits', {
            folder: folderIndex?.folder || 'unknown',
            retainedSamples: clampedSamples.length,
        });
    }

    const expectedCount = Array.isArray(folderIndex?.commits)
        ? folderIndex.commits.length
        : 0;
    const missingSampleCount = Math.max(
        0,
        expectedCount - originalLength,
    );

    const series = createEmptySeries();
    series.allSamples = clampedSamples;
    series.gaps = missingSampleCount;
    series.truncated = truncated;
    series.missingSampleCount = missingSampleCount;

    const initialWindow = loadStoredWindowMode();
    updateSeriesWindow(series, initialWindow);

    return series;
}

/**
 * Render the history chart inside the provided container.
 * @param {object} series Hydrated history series
 * @param {HTMLElement} container DOM element where the chart should render
 */
function renderHistoryChart(series, container, options = {}) {
    if (!container) {
        console.error('history-chart: renderHistoryChart requires a canvas element');
        return null;
    }
    if (typeof Chart === 'undefined') {
        console.error('history-chart: Chart.js not found on window');
        return null;
    }
    const { emptyStateElement, tooltipElement } = options;

    const canMeasurePerformance =
        typeof performance !== 'undefined' &&
        typeof performance.mark === 'function' &&
        typeof performance.measure === 'function';
    const startMark = canMeasurePerformance ? 'history-chart-render-start' : null;
    const endMark = canMeasurePerformance ? 'history-chart-render-end' : null;
    const measureName = 'history-chart-render';

    if (canMeasurePerformance) {
        performance.mark(startMark);
    }

    const existingChart = container.__historyChartInstance;
    if (existingChart) {
        existingChart.destroy();
        container.__historyChartInstance = null;
    }

    if (!series?.samples?.length) {
        if (emptyStateElement) {
            emptyStateElement.hidden = false;
            emptyStateElement.textContent =
                'History data not available for this folder.';
        }
        updateHistoryTooltip(series, tooltipElement, -1);
        container.setAttribute(
            'aria-label',
            'History chart unavailable: no commit samples found.',
        );
        const ctx = container.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, container.width, container.height);
        }
        if (canMeasurePerformance) {
            performance.mark(endMark);
            performance.measure(measureName, startMark, endMark);
            const [entry] = performance.getEntriesByName(measureName).slice(-1);
            const durationMs = entry?.duration ?? 0;
            console.info('history-chart: render skipped (no data)', {
                durationMs: durationMs.toFixed(2),
                sampleCount: 0,
            });
            performance.clearMarks(startMark);
            performance.clearMarks(endMark);
            performance.clearMeasures(measureName);
        }
        return null;
    }

    if (emptyStateElement) {
        const messages = [];
        if (series.samples.length < 5) {
            messages.push(
                'More history needed. At least 5 commits are recommended to view trends.',
            );
        }
        if (series.truncated) {
            messages.push(
                'Showing the most recent 180 commits; older history is truncated.',
            );
        }
        if ((series.gaps ?? 0) > 0) {
            messages.push(
                `${series.gaps} commit entries were skipped due to missing timestamps or artifacts.`,
            );
        }
        if (messages.length) {
            emptyStateElement.hidden = false;
            emptyStateElement.textContent = messages.join(' ');
        } else {
            emptyStateElement.hidden = true;
            emptyStateElement.textContent = '';
        }
        if (series.truncated) {
            emptyStateElement.dataset.truncated = 'true';
        } else {
            delete emptyStateElement.dataset.truncated;
        }
    }

    const labels = series.samples.map((sample) =>
        new Date(sample.committedAtEpochMs).toLocaleString(),
    );
    const data = series.samples.map((sample) => sample.totalSizeBytes / 1024);

    const ctx = container.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Total size (KB)',
                    data,
                    borderColor: '#2563eb',
                    borderWidth: 2,
                    backgroundColor: 'rgba(37, 99, 235, 0.12)',
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    tension: 0.25,
                    fill: true,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    ticks: {
                        callback: (value) => {
                            const numeric = Number(value);
                            if (!Number.isFinite(numeric)) {
                                return `${value}`;
                            }
                            if (numeric >= 1024) {
                                return `${(numeric / 1024).toFixed(1)} MB`;
                            }
                            return `${numeric.toFixed(1)} KB`;
                        },
                    },
                    title: {
                        display: true,
                        text: 'Total artifact size (KB / MB)',
                    },
                },
                x: {
                    ticks: {
                        maxRotation: 35,
                        minRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 10,
                    },
                },
            },
            plugins: {
                tooltip: {
                    enabled: false,
                },
                legend: {
                    labels: {
                        usePointStyle: true,
                    },
                },
            },
        },
    });

    container.__historyChartInstance = chart;
    container.setAttribute('aria-label', describeSeries(series));

    if (tooltipElement) {
        updateHistoryTooltip(series, tooltipElement, series.samples.length - 1);
    }

    if (canMeasurePerformance) {
        performance.mark(endMark);
        performance.measure(measureName, startMark, endMark);
        const [entry] = performance.getEntriesByName(measureName).slice(-1);
        const durationMs = entry?.duration ?? 0;
        console.info('history-chart: render complete', {
            durationMs: durationMs.toFixed(2),
            sampleCount: series.samples.length,
            gaps: series.gaps ?? 0,
            truncated: Boolean(series.truncated),
        });
        performance.clearMarks(startMark);
        performance.clearMarks(endMark);
        performance.clearMeasures(measureName);
    }

    return chart;
}
function attachHistoryControls(series, controlsRoot, options = {}) {
    if (!controlsRoot) {
        console.error('history-chart: attachHistoryControls requires a container');
        return;
    }

    const { onSampleFocus } = options;

    const windowContainerSelector = '[data-role="history-windows"]';
    const pointsContainerSelector = '[data-role="history-points"]';

    let windowsContainer = controlsRoot.querySelector(windowContainerSelector);
    if (!windowsContainer) {
        windowsContainer = document.createElement('div');
        windowsContainer.dataset.role = 'history-windows';
        windowsContainer.className = 'history-controls__windows';
        controlsRoot.appendChild(windowsContainer);
    }

    let pointsContainer = controlsRoot.querySelector(pointsContainerSelector);
    if (!pointsContainer) {
        pointsContainer = document.createElement('div');
        pointsContainer.dataset.role = 'history-points';
        pointsContainer.className = 'history-controls__points';
        controlsRoot.appendChild(pointsContainer);
    }

    const renderWindowButtons = () => {
        windowsContainer.innerHTML = '';
        const introLabel =
            controlsRoot.querySelector('#history-window-label') || null;
        if (introLabel) {
            windowsContainer.setAttribute('aria-labelledby', introLabel.id);
        } else {
            const generatedLabel = document.createElement('span');
            generatedLabel.id = 'history-window-chip-label';
            generatedLabel.textContent = 'Window:';
            windowsContainer.appendChild(generatedLabel);
            windowsContainer.setAttribute('aria-labelledby', generatedLabel.id);
        }
        windowsContainer.setAttribute('role', 'group');

        WINDOW_OPTIONS.forEach((windowMode) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.window = windowMode;
            button.setAttribute(
                'aria-pressed',
                series.windowMode === windowMode ? 'true' : 'false',
            );
            button.textContent = `${windowMode} commits`;
            button.addEventListener('click', () => {
                if (series.windowMode === windowMode) {
                    return;
                }
                updateSeriesWindow(series, windowMode);
                persistWindowMode(windowMode);
                renderWindowButtons();
                renderPointButtons();
                if (typeof options.onWindowChange === 'function') {
                    options.onWindowChange(windowMode, series);
                }
            });
            windowsContainer.appendChild(button);
        });
    };

    let pointButtons = [];
    let activeIndex = -1;

    const setActive = (nextActiveIndex, emit = true) => {
        if (nextActiveIndex == null || !Number.isFinite(nextActiveIndex)) {
            return;
        }
        if (!pointButtons.length) {
            activeIndex = -1;
            return;
        }
        const clampedIndex = Math.max(
            0,
            Math.min(pointButtons.length - 1, nextActiveIndex),
        );
        activeIndex = clampedIndex;
        pointButtons.forEach((button, index) => {
            const pressed = index === activeIndex;
            button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
            button.classList.toggle('history-controls__point--active', pressed);
        });
        const sample = series.samples?.[activeIndex];
        if (emit && sample && typeof onSampleFocus === 'function') {
            onSampleFocus(activeIndex, sample);
        }
    };

    const focusSampleAt = (index) => {
        if (index < 0 || index >= pointButtons.length) {
            return;
        }
        pointButtons[index].focus();
    };

    const handleKeyNavigation = (event, currentIndex) => {
        const { key } = event;
        if (!['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(key)) {
            return;
        }
        event.preventDefault();
        if (key === 'Home') {
            focusSampleAt(0);
            return;
        }
        if (key === 'End') {
            focusSampleAt(pointButtons.length - 1);
            return;
        }
        if (key === ' ' || key === 'Spacebar' || key === 'Enter') {
            event.preventDefault();
            setActive(currentIndex);
            return;
        }
        const direction = key === 'ArrowRight' || key === 'ArrowDown' ? 1 : -1;
        const nextIndex = Math.min(
            pointButtons.length - 1,
            Math.max(0, currentIndex + direction),
        );
        focusSampleAt(nextIndex);
    };

    const setupScrollInteractions = () => {
        if (!pointsContainer || pointsContainer.dataset.scrollSetup === 'true') {
            return;
        }
        pointsContainer.dataset.scrollSetup = 'true';

        let pointerActive = false;
        let pointerId = null;
        let startX = 0;
        let scrollOrigin = 0;
        let moved = false;

        const endDrag = (event) => {
            if (!pointerActive || (event.pointerId != null && event.pointerId !== pointerId)) {
                return;
            }
            if (moved) {
                event.preventDefault();
            }
            try {
                if (pointerId != null && pointsContainer.hasPointerCapture?.(pointerId)) {
                    pointsContainer.releasePointerCapture(pointerId);
                }
            } catch (error) {
                void error;
            }
            pointsContainer.classList.remove('history-controls__points--dragging');
            pointerActive = false;
            pointerId = null;
            moved = false;
        };

        pointsContainer.addEventListener('pointerdown', (event) => {
            if (event.button !== undefined && event.button !== 0 && event.pointerType !== 'touch') {
                return;
            }
            pointerActive = true;
            pointerId = event.pointerId;
            startX = event.clientX;
            scrollOrigin = pointsContainer.scrollLeft;
            moved = false;
        });

        pointsContainer.addEventListener('pointermove', (event) => {
            if (!pointerActive || event.pointerId !== pointerId) {
                return;
            }
            const deltaX = event.clientX - startX;
            if (!moved && Math.abs(deltaX) > 4) {
                moved = true;
                pointsContainer.classList.add('history-controls__points--dragging');
                try {
                    pointsContainer.setPointerCapture(pointerId);
                } catch (error) {
                    void error;
                }
            }
            if (moved) {
                event.preventDefault();
                pointsContainer.scrollLeft = scrollOrigin - deltaX;
            }
        });

        const cancelDrag = (event) => {
            endDrag(event);
        };

        pointsContainer.addEventListener('pointerup', cancelDrag);
        pointsContainer.addEventListener('pointercancel', cancelDrag);
        pointsContainer.addEventListener('pointerleave', cancelDrag);

        pointsContainer.addEventListener(
            'wheel',
            (event) => {
                if (pointsContainer.scrollWidth <= pointsContainer.clientWidth) {
                    return;
                }
                const dominantDelta =
                    Math.abs(event.deltaY) >= Math.abs(event.deltaX)
                        ? event.deltaY
                        : event.deltaX;
                if (!dominantDelta) {
                    return;
                }
                event.preventDefault();
                pointsContainer.scrollLeft += dominantDelta;
            },
            { passive: false },
        );
    };

    setupScrollInteractions();

    const renderPointButtons = () => {
        const previousScrollLeft = pointsContainer.scrollLeft;
        pointsContainer.innerHTML = '';
        pointButtons = [];

        if (!series?.samples?.length) {
            const message = document.createElement('p');
            message.className = 'history-controls__message';
            message.textContent =
                'History focus navigation is unavailable for this folder.';
            pointsContainer.appendChild(message);
            return;
        }

        series.samples.forEach((sample, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'history-controls__point';
            button.dataset.sampleIndex = String(index);
            const labelDate = new Date(sample.committedAtEpochMs).toLocaleDateString();
            const message = sample.metadata?.message || '';
            const pointInner = document.createElement('span');
            pointInner.className = 'history-controls__point-inner';
            const metaRow = document.createElement('span');
            metaRow.className = 'history-controls__point-meta';
            const badgeText = (() => {
                const kind = (sample.metadata?.kind || '').toLowerCase();
                if (kind === 'head') {
                    return 'HEAD';
                }
                if (kind === 'master') {
                    return 'MASTER';
                }
                return null;
            })();
            if (badgeText) {
                const badgeEl = document.createElement('span');
                badgeEl.className = 'history-controls__point-badge';
                badgeEl.textContent = badgeText;
                metaRow.appendChild(badgeEl);
            }
            const dateEl = document.createElement('span');
            dateEl.className = 'history-controls__point-date';
            dateEl.textContent = labelDate;
            metaRow.appendChild(dateEl);
            const messageEl = document.createElement('span');
            messageEl.className = 'history-controls__point-message';
            messageEl.textContent = message || '—';
            pointInner.appendChild(metaRow);
            pointInner.appendChild(messageEl);
            button.appendChild(pointInner);
            const kindLabel = badgeText ? `${badgeText} commit, ` : '';
            button.setAttribute(
                'aria-label',
                `Commit ${sample.metadata?.gitSha?.slice(0, 7) || 'UNKNOWN'}, ${kindLabel}${message || 'no commit message'} on ${new Date(
                    sample.committedAtEpochMs,
                ).toLocaleString()}. Size ${formatSizeKb(sample.totalSizeBytes)}.`,
            );
            button.setAttribute('aria-pressed', 'false');
            button.addEventListener('click', () => {
                setActive(index);
            });
            button.addEventListener('keydown', (event) => {
                handleKeyNavigation(event, index);
            });

            pointButtons.push(button);
            pointsContainer.appendChild(button);
        });

        if (activeIndex >= 0) {
            setActive(activeIndex, false);
        }

        const maxScrollLeft = Math.max(
            0,
            pointsContainer.scrollWidth - pointsContainer.clientWidth,
        );
        if (maxScrollLeft > 0) {
            pointsContainer.scrollLeft = Math.min(previousScrollLeft, maxScrollLeft);
        }

        return pointButtons;
    };

    renderWindowButtons();
    renderPointButtons();

    return {
        focus(index) {
            if (index == null || !Number.isFinite(index)) {
                return;
            }
            const button = pointButtons[index];
            if (!button) {
                return;
            }
            button.focus();
            setActive(index);
        },
    };
}

const __historyChartScaffold = {
    HISTORY_DEFAULT_WINDOW,
    WINDOW_OPTIONS,
    MAX_HISTORY_SAMPLES,
    createEmptySeries,
    normalizeWindowMode,
};

window.historyChart = {
    hydrateHistorySeries,
    renderHistoryChart,
    attachHistoryControls,
    updateHistoryTooltip,
    __historyChartScaffold,
};

})();
