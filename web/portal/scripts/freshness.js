(() => {
    const MANIFEST_URL = 'manifest.json';
    const SIZE_INDEX_URL = 'reports/size/index.json';

    const sandboxLink = document.getElementById('sandbox-link');
    const reportLink = document.getElementById('report-link');
    const sandboxStatus = document.querySelector('[data-role="sandbox-status"]');
    const reportStatus = document.querySelector('[data-role="report-status"]');
    const metricsStatus = document.querySelector('[data-role="metrics-status"]');
    const metricsFields = {
        commitMessage: document.querySelector('[data-role="commit-message"]'),
        commitHash: document.querySelector('[data-role="commit-hash"]'),
        generatedAt: document.querySelector('[data-role="generated-at"]'),
        artifactTable: document.querySelector('[data-role="artifact-table"]'),
    };
    const deploymentRuntime = document.querySelector('[data-role="deployment-runtime"]');

    function setStatus(el, message, status) {
        if (!el) return;
        el.textContent = message || '';
        if (status) {
            el.dataset.status = status;
        } else {
            delete el.dataset.status;
        }
    }

    function formatDate(value) {
        if (!value) return '—';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString();
    }

    function formatSize(value) {
        if (typeof value !== 'number' || Number.isNaN(value)) return '—';
        return value.toFixed(2);
    }

    function formatRuntime(ms) {
        if (typeof ms !== 'number' || Number.isNaN(ms)) return '—';
        if (ms < 1000) return `${ms.toFixed(0)} ms`;
        return `${(ms / 1000).toFixed(2)} s`;
    }

    function formatSha(value) {
        if (!value) return '—';
        return value.length > 12 ? value.slice(0, 12) : value;
    }

    async function loadManifest() {
        let manifest = null;
        try {
            const response = await fetch(MANIFEST_URL, { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`Failed to load manifest: ${response.status}`);
            }
            manifest = await response.json();
            applyManifest(manifest);
        } catch (error) {
            console.error(error);
            setStatus(sandboxStatus, 'Unable to load manifest metadata.', 'error');
            setStatus(reportStatus, 'Unable to load manifest metadata.', 'error');
            setStatus(metricsStatus, 'Metrics unavailable.', 'error');
        }
        hydrateMetricsFromReports().catch((error) => {
            console.warn('Unable to derive build metrics from reports.', error);
        });
    }

    function applyManifest(manifest) {
        const sandbox = manifest?.sandbox;
        const report = manifest?.report;
        const metrics = manifest?.metrics;

        if (sandbox?.url) {
            sandboxLink.href = sandbox.url;
            sandboxLink.textContent = 'Launch Sandbox';
            sandboxLink.setAttribute('aria-disabled', 'false');
            setStatus(
                sandboxStatus,
                `Ready · ${formatSize(sandbox?.sizeKb ?? NaN)} KB · checksum ${sandbox?.sha256?.slice(0, 8) ?? '—'}`,
                'success',
            );
        } else {
            sandboxLink.removeAttribute('href');
            sandboxLink.setAttribute('aria-disabled', 'true');
            sandboxLink.textContent = 'Unavailable';
            setStatus(sandboxStatus, 'Sandbox artifact missing.', 'error');
        }

        if (report?.url) {
            reportLink.href = report.url;
            reportLink.textContent = 'Open Report';
            reportLink.setAttribute('aria-disabled', 'false');
            setStatus(
                reportStatus,
                `Ready · ${formatSize(report?.sizeKb ?? NaN)} KB · checksum ${report?.sha256?.slice(0, 8) ?? '—'}`,
                'success',
            );
        } else {
            reportLink.removeAttribute('href');
            reportLink.setAttribute('aria-disabled', 'true');
            reportLink.textContent = 'Unavailable';
            setStatus(reportStatus, 'Size report artifact missing.', 'error');
        }

        if (metrics) {
            let manifestArtifacts;
            if (Array.isArray(metrics.artifacts)) {
                manifestArtifacts = metrics.artifacts.map((artifact) => ({
                    name: artifact.name ?? artifact.file ?? 'artifact',
                    sizeKb: artifact.sizeKb ?? artifact.size_kb ?? null,
                }));
            }
            updateMetricsFields({
                commitMessage: metrics.commitMessage ?? null,
                commitHash: metrics.commitHash ?? manifest?.commitHash ?? null,
                generatedAt: manifest?.generatedAt ?? null,
                artifacts: manifestArtifacts,
                status: metrics.status ?? undefined,
                statusMessage: metrics.statusMessage ?? undefined,
            });
        } else {
            updateMetricsFields({
                commitMessage: null,
                commitHash: manifest?.commitHash ?? null,
                generatedAt: manifest?.generatedAt ?? null,
                artifacts: undefined,
                status: 'warning',
                statusMessage: 'Metrics unavailable.',
            });
        }

        deploymentRuntime.textContent = formatRuntime(manifest?.deploymentRuntimeMs);
    }

    function updateMetricsFields({ commitMessage, commitHash, generatedAt, artifacts, status, statusMessage }) {
        if (commitMessage !== undefined) {
            metricsFields.commitMessage.textContent = commitMessage ?? '—';
        }
        if (commitHash !== undefined) {
            if (commitHash) {
                metricsFields.commitHash.textContent = formatSha(commitHash);
                metricsFields.commitHash.title = commitHash;
            } else {
                metricsFields.commitHash.textContent = '—';
                metricsFields.commitHash.removeAttribute('title');
            }
        }
        if (generatedAt !== undefined) {
            metricsFields.generatedAt.textContent = formatDate(generatedAt);
        }
        if (artifacts !== undefined) {
            renderArtifactTable(artifacts);
        }
        if (status !== undefined || statusMessage !== undefined) {
            setStatus(metricsStatus, statusMessage ?? '', status);
        }
    }

    function renderArtifactTable(artifacts) {
        const tbody = metricsFields.artifactTable;
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!Array.isArray(artifacts) || artifacts.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 2;
            cell.textContent = 'No artifact data.';
            row.appendChild(cell);
            tbody.appendChild(row);
            return;
        }

        artifacts.forEach(({ name, sizeKb }) => {
            const row = document.createElement('tr');

            const nameCell = document.createElement('td');
            nameCell.textContent = name || '—';
            row.appendChild(nameCell);

            const sizeCell = document.createElement('td');
            sizeCell.textContent =
                typeof sizeKb === 'number' && !Number.isNaN(sizeKb) ? formatSize(sizeKb) : '—';
            row.appendChild(sizeCell);

            tbody.appendChild(row);
        });
    }

    async function hydrateMetricsFromReports() {
        const indexResponse = await fetch(SIZE_INDEX_URL, { cache: 'no-store' });
        if (!indexResponse.ok) {
            throw new Error(`Unable to load ${SIZE_INDEX_URL}: ${indexResponse.status}`);
        }
        const indexManifest = await indexResponse.json();
        const targetFolder =
            indexManifest.folders?.find((folder) => folder.folder === 'sandbox/wasm/release') ??
            indexManifest.folders?.[0];
        if (!targetFolder) {
            throw new Error('No folders defined in reports/size index.');
        }
        const releaseUrl = `reports/size/${targetFolder.index}`;
        const releaseResponse = await fetch(releaseUrl, { cache: 'no-store' });
        if (!releaseResponse.ok) {
            throw new Error(`Unable to load ${releaseUrl}: ${releaseResponse.status}`);
        }
        const releaseIndex = await releaseResponse.json();
        const [headCommit, previousCommit] = releaseIndex.commits ?? [];
        if (!headCommit) {
            throw new Error('Release index missing head commit.');
        }
        const artifactMetrics = buildArtifactMetrics(headCommit, previousCommit);

        updateMetricsFields({
            commitHash: headCommit.git_sha ?? headCommit.label ?? null,
            generatedAt: headCommit.date ?? releaseIndex.generated_at ?? indexManifest.generated_at ?? null,
            artifacts: artifactMetrics,
            status: 'success',
        });
    }

    function buildArtifactMetrics(headCommit, previousCommit) {
        if (!headCommit?.artifacts) {
            return [];
        }
        return headCommit.artifacts
            .map((artifact) => {
                const sizeBytes = typeof artifact.size_bytes === 'number' ? artifact.size_bytes : null;
                return {
                    name: artifact.file_name || artifact.label || 'artifact',
                    sizeKb: sizeBytes != null ? sizeBytes / 1024 : null,
                };
            })
            .sort((a, b) => {
                if (!a.name) return -1;
                if (!b.name) return 1;
                return a.name.localeCompare(b.name);
            });
    }

    loadManifest().catch((error) => {
        console.error('Failed to initialise portal manifest', error);
    });
})();
