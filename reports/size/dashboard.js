const SUMMARY_URL = 'index.json';
const TABLE_BODY = document.querySelector('#artifact-table tbody');
const EMPTY_STATE = document.getElementById('empty-state');
const FOLDER_SELECT = document.getElementById('folder-select');
const GENERATED_AT = document.getElementById('generated-at');
const COMMIT_BASE_SELECT = document.getElementById('commit-base-select');
const COMMIT_TARGET_SELECT = document.getElementById('commit-target-select');
const COMMIT_BASE_SHA = document.getElementById('commit-base-sha');
const COMMIT_BASE_MESSAGE = document.getElementById('commit-base-message');
const COMMIT_BASE_DATE = document.getElementById('commit-base-date');
const COMMIT_TARGET_SHA = document.getElementById('commit-target-sha');
const COMMIT_TARGET_MESSAGE = document.getElementById('commit-target-message');
const COMMIT_TARGET_DATE = document.getElementById('commit-target-date');
const ALERT_COUNT = document.getElementById('alert-count');
const BASE_HEADER = document.getElementById('commit-base-column');
const TARGET_HEADER = document.getElementById('commit-target-column');
const CHART_CANVAS = document.getElementById('size-chart');

const state = {
    summary: null,
    folderCache: new Map(),
    currentFolderIndex: 0,
    currentCommits: [],
    selectedBaseId: null,
    selectedTargetId: null,
    chart: null,
};

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

function formatDelta(value) {
    const sign = value > 0 ? '+' : '';
    return `${sign}${formatNumber(value)}`;
}

function formatPercent(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '—';
    }
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}

function shortenSha(sha) {
    if (!sha || sha === 'UNKNOWN') {
        return 'UNKNOWN';
    }
    return sha.length <= 7 ? sha : sha.slice(0, 7);
}

function formatCommitLabel(commit) {
    if (!commit) {
        return 'Unknown';
    }
    const dateLabel = commit.date ? ` (${formatDate(commit.date)})` : '';
    if (commit.label) {
        return `${commit.label}${dateLabel}`;
    }
    const kind = (commit.kind || '').toUpperCase();
    const sha = shortenSha(commit.git_sha || 'UNKNOWN');
    if (kind) {
        return `${kind} — ${sha}${dateLabel}`;
    }
    const message = commit.git_message && commit.git_message !== 'UNKNOWN' ? commit.git_message : '';
    const baseLabel = message ? `${sha} — ${message}` : sha;
    return `${baseLabel}${dateLabel}`;
}

function getCommitId(commit) {
    if (!commit) {
        return '';
    }
    if (commit.id) {
        return commit.id;
    }
    const kind = commit.kind || 'commit';
    const sha = commit.git_sha || 'UNKNOWN';
    return `${kind}:${sha}`;
}

function formatDate(value) {
    if (!value) {
        return '—';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }
    return date.toLocaleString();
}

function populateFolderOptions(folders) {
    FOLDER_SELECT.innerHTML = '';
    folders.forEach((entry, index) => {
        const option = document.createElement('option');
        option.value = index.toString();
        option.textContent = entry.folder;
        FOLDER_SELECT.appendChild(option);
    });
}

function populateCommitSelectors(commits) {
    COMMIT_BASE_SELECT.innerHTML = '';
    COMMIT_TARGET_SELECT.innerHTML = '';

    commits.forEach((commit) => {
        const optionA = document.createElement('option');
        optionA.value = getCommitId(commit);
        optionA.textContent = formatCommitLabel(commit);
        COMMIT_BASE_SELECT.appendChild(optionA);

        const optionB = document.createElement('option');
        optionB.value = getCommitId(commit);
        optionB.textContent = formatCommitLabel(commit);
        COMMIT_TARGET_SELECT.appendChild(optionB);
    });

    const headCommit = commits.find((commit) => commit.kind === 'head') || commits[0] || null;
    const branchCommits = commits.filter((commit) => commit.kind === 'branch');
    const branchCommitDifferent =
        headCommit ?
            branchCommits.find((commit) => getCommitId(commit) !== getCommitId(headCommit)) || null :
            null;
    const branchCommitAny = branchCommits[0] || null;

    const defaultBase = branchCommitDifferent || branchCommitAny || headCommit;
    const defaultTarget = headCommit || defaultBase;

    state.selectedBaseId = defaultBase ? getCommitId(defaultBase) : null;
    state.selectedTargetId = defaultTarget ? getCommitId(defaultTarget) : state.selectedBaseId;

    if (state.selectedBaseId) {
        COMMIT_BASE_SELECT.value = state.selectedBaseId;
    }
    if (state.selectedTargetId) {
        COMMIT_TARGET_SELECT.value = state.selectedTargetId;
    }

    const disabled = commits.length === 0;
    COMMIT_BASE_SELECT.disabled = disabled;
    COMMIT_TARGET_SELECT.disabled = disabled;
}

function findCommitById(commits, id) {
    if (!id) {
        return null;
    }
    return commits.find((commit) => getCommitId(commit) === id) || null;
}

function computeComparison(baseCommit, targetCommit) {
    if (!baseCommit || !targetCommit) {
        return { rows: [], alertCount: 0 };
    }

    const baseMap = new Map();
    const targetMap = new Map();

    (baseCommit.artifacts || []).forEach((artifact) => {
        baseMap.set(artifact.file_name, artifact.size_bytes);
    });
    (targetCommit.artifacts || []).forEach((artifact) => {
        targetMap.set(artifact.file_name, artifact.size_bytes);
    });

    const fileNames = new Set([...baseMap.keys(), ...targetMap.keys()]);
    const rows = [];
    let alertCount = 0;

    Array.from(fileNames)
        .sort((a, b) => a.localeCompare(b))
        .forEach((fileName) => {
            const baseSize = baseMap.get(fileName) ?? 0;
            const targetSize = targetMap.get(fileName) ?? 0;
            const deltaBytes = targetSize - baseSize;
            let deltaPercent = null;
            if (baseSize > 0) {
                deltaPercent = (deltaBytes / baseSize) * 100;
            } else if (targetSize > 0) {
                deltaPercent = 100;
            }
            const exceedsBytes = Math.abs(deltaBytes) >= 25_000;
            const exceedsPercent = deltaPercent !== null && Math.abs(deltaPercent) >= 2;
            const alert = exceedsBytes || exceedsPercent;
            if (alert) {
                alertCount += 1;
            }
            rows.push({
                file_name: fileName,
                base_size: baseSize,
                target_size: targetSize,
                delta_bytes: deltaBytes,
                delta_percent: deltaPercent,
                alert,
            });
        });

    return { rows, alertCount };
}

function updateSummary(baseCommit, targetCommit, alertCount) {
    COMMIT_BASE_SHA.textContent = baseCommit?.git_sha || 'UNKNOWN';
    COMMIT_BASE_MESSAGE.textContent = baseCommit?.git_message || '—';
    COMMIT_BASE_DATE.textContent = baseCommit ? formatDate(baseCommit.date) : '—';
    COMMIT_TARGET_SHA.textContent = targetCommit?.git_sha || 'UNKNOWN';
    COMMIT_TARGET_MESSAGE.textContent = targetCommit?.git_message || '—';
    COMMIT_TARGET_DATE.textContent = targetCommit ? formatDate(targetCommit.date) : '—';
    ALERT_COUNT.textContent = alertCount.toString();
}

function renderTable(rows, baseCommit, targetCommit) {
    TABLE_BODY.innerHTML = '';

    const baseLabel = formatCommitLabel(baseCommit);
    const targetLabel = formatCommitLabel(targetCommit);
    BASE_HEADER.textContent = `${baseLabel} (bytes)`;
    TARGET_HEADER.textContent = `${targetLabel} (bytes)`;

    if (!rows.length) {
        EMPTY_STATE.hidden = false;
        return;
    }

    EMPTY_STATE.hidden = true;

    rows.forEach((artifact) => {
        const row = document.createElement('tr');
        if (artifact.alert) {
            row.classList.add('alert');
        }

        row.innerHTML = `
            <td>${artifact.file_name || '<em>(missing)</em>'}</td>
            <td>${formatNumber(artifact.base_size ?? 0)}</td>
            <td>${formatNumber(artifact.target_size ?? 0)}</td>
            <td>${formatDelta(artifact.delta_bytes ?? 0)}</td>
            <td>${formatPercent(artifact.delta_percent)}</td>
            <td>${renderStatusBadge(artifact.alert)}</td>
        `;

        TABLE_BODY.appendChild(row);
    });
}

function renderStatusBadge(isAlert) {
    const statusClass = isAlert ? 'alert' : 'ok';
    const text = isAlert ? 'Alert' : 'OK';
    return `<span class="status-badge ${statusClass}">${text}</span>`;
}

function renderChart(rows, baseCommit, targetCommit) {
    if (state.chart) {
        state.chart.destroy();
        state.chart = null;
    }

    if (!rows.length) {
        return;
    }

    const labels = rows.map((artifact) => artifact.file_name);
    const baseData = rows.map((artifact) => artifact.base_size ?? 0);
    const targetData = rows.map((artifact) => artifact.target_size ?? 0);

    const ctx = CHART_CANVAS.getContext('2d');
    state.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: formatCommitLabel(baseCommit),
                    backgroundColor: '#94a3b8',
                    data: baseData,
                },
                {
                    label: formatCommitLabel(targetCommit),
                    backgroundColor: '#2563eb',
                    data: targetData,
                },
            ],
        },
    });
}

function updateGeneratedAt(summary) {
    if (!summary || !summary.generated_at) {
        GENERATED_AT.textContent = '';
        return;
    }
    const date = new Date(summary.generated_at);
    GENERATED_AT.textContent = `Generated: ${date.toLocaleString()}`;
}

async function fetchSummary() {
    const response = await fetch(SUMMARY_URL, { cache: 'no-cache' });
    if (!response.ok) {
        throw new Error(`Failed to load ${SUMMARY_URL}: ${response.status}`);
    }
    return response.json();
}

async function ensureCommits(entry) {
    if (!entry) {
        return [];
    }
    if (state.folderCache.has(entry.folder)) {
        return state.folderCache.get(entry.folder);
    }
    const response = await fetch(entry.index, { cache: 'no-cache' });
    if (!response.ok) {
        throw new Error(`Failed to load ${entry.index}: ${response.status}`);
    }
    const data = await response.json();
    const commits = data.commits || [];
    state.folderCache.set(entry.folder, commits);
    return commits;
}

function renderDashboard() {
    const commits = state.currentCommits;
    if (!commits.length) {
        TABLE_BODY.innerHTML = '';
        EMPTY_STATE.hidden = false;
        COMMIT_BASE_SHA.textContent = 'UNKNOWN';
        COMMIT_BASE_MESSAGE.textContent = '—';
        COMMIT_BASE_DATE.textContent = '—';
        COMMIT_TARGET_SHA.textContent = 'UNKNOWN';
        COMMIT_TARGET_MESSAGE.textContent = '—';
        COMMIT_TARGET_DATE.textContent = '—';
        ALERT_COUNT.textContent = '0';
        if (state.chart) {
            state.chart.destroy();
            state.chart = null;
        }
        return;
    }

    let baseCommit = findCommitById(commits, state.selectedBaseId) || commits[0];
    let targetCommit =
        findCommitById(commits, state.selectedTargetId) || commits[(commits.length > 1 ? 1 : 0)] || baseCommit;

    state.selectedBaseId = getCommitId(baseCommit);
    state.selectedTargetId = getCommitId(targetCommit);
    COMMIT_BASE_SELECT.value = state.selectedBaseId;
    COMMIT_TARGET_SELECT.value = state.selectedTargetId;

    const comparison = computeComparison(baseCommit, targetCommit);
    updateSummary(baseCommit, targetCommit, comparison.alertCount);
    renderTable(comparison.rows, baseCommit, targetCommit);
    renderChart(comparison.rows, baseCommit, targetCommit);
}

async function selectFolder(index) {
    const entry = state.summary.folders[index];
    if (!entry) {
        return;
    }
    state.currentFolderIndex = index;
    const commits = await ensureCommits(entry);
    state.currentCommits = commits;
    populateCommitSelectors(commits);
    renderDashboard();
}

async function bootstrap() {
    try {
        const summary = await fetchSummary();
        if (!summary.folders || summary.folders.length === 0) {
            throw new Error('No folders available in manifest');
        }
        state.summary = summary;
        updateGeneratedAt(summary);
        populateFolderOptions(summary.folders);
        FOLDER_SELECT.value = '0';
        await selectFolder(0);
    } catch (error) {
        console.error(error);
        TABLE_BODY.innerHTML = '<tr><td colspan="6">Failed to load size data.</td></tr>';
        EMPTY_STATE.hidden = true;
    }
}

FOLDER_SELECT.addEventListener('change', (event) => {
    const index = Number(event.target.value);
    selectFolder(Number.isNaN(index) ? 0 : index).catch((error) => {
        console.error(error);
    });
});

COMMIT_BASE_SELECT.addEventListener('change', (event) => {
    state.selectedBaseId = event.target.value;
    renderDashboard();
});

COMMIT_TARGET_SELECT.addEventListener('change', (event) => {
    state.selectedTargetId = event.target.value;
    renderDashboard();
});

window.addEventListener('DOMContentLoaded', () => {
    bootstrap().catch((error) => console.error(error));
});
