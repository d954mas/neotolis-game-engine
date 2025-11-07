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
        wasmSize: document.querySelector('[data-role="wasm-size"]'),
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
            updateMetricsFields({
                commitMessage: metrics.commitMessage ?? null,
                commitHash: metrics.commitHash ?? manifest?.commitHash ?? null,
                generatedAt: manifest?.generatedAt ?? null,
                wasmSizeKb: metrics.wasmSizeKb,
                status: metrics.status ?? undefined,
                statusMessage: metrics.statusMessage ?? undefined,
            });
        } else {
            updateMetricsFields({
                commitMessage: null,
                commitHash: manifest?.commitHash ?? null,
                generatedAt: manifest?.generatedAt ?? null,
                status: 'warning',
                statusMessage: 'Metrics unavailable.',
            });
        }

        deploymentRuntime.textContent = formatRuntime(manifest?.deploymentRuntimeMs);
    }

    function updateMetricsFields({ commitMessage, commitHash, generatedAt, wasmSizeKb, status, statusMessage }) {
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
        if (wasmSizeKb !== undefined) {
            metricsFields.wasmSize.textContent =
                typeof wasmSizeKb === 'number' && !Number.isNaN(wasmSizeKb) ? formatSize(wasmSizeKb) : '—';
        }
        if (status !== undefined || statusMessage !== undefined) {
            setStatus(metricsStatus, statusMessage ?? '', status);
        }
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
        const wasmEntry =
            headCommit.artifacts?.find((artifact) => artifact.file_name?.endsWith('.wasm')) ?? null;
        let prevWasm = null;
        if (wasmEntry && previousCommit) {
            prevWasm = previousCommit.artifacts?.find((artifact) => artifact.file_name === wasmEntry.file_name) ?? null;
        }
        const deltaBytes =
            wasmEntry && prevWasm && typeof wasmEntry.size_bytes === 'number' && typeof prevWasm.size_bytes === 'number'
                ? wasmEntry.size_bytes - prevWasm.size_bytes
                : null;
        const wasmDeltaKb = deltaBytes != null ? deltaBytes / 1024 : null;
        const microbenchMs =
            typeof headCommit.microbench_ms === 'number' ? headCommit.microbench_ms : undefined;

        updateMetricsFields({
            commitHash: headCommit.git_sha ?? headCommit.label ?? null,
            generatedAt: headCommit.date ?? releaseIndex.generated_at ?? indexManifest.generated_at ?? null,
            wasmDeltaKb,
            microbenchMs,
            status: 'success',
            statusMessage: `Metrics derived from ${targetFolder.folder}`,
        });
    }

    loadManifest().catch((error) => {
        console.error('Failed to initialise portal manifest', error);
    });
})();
