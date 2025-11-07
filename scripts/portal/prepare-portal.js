#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');

async function main() {
    const args = parseArgs(process.argv.slice(2));
    if (!args.sandbox) {
        throw new Error('Missing required --sandbox <path> argument pointing to the sandbox artifact directory.');
    }
    if (!args.report) {
        throw new Error('Missing required --report <path> argument pointing to the reports/size directory.');
    }

    const portalRoot = path.resolve(args.output ?? path.join(process.cwd(), 'web/portal'));
    const sandboxSource = path.resolve(args.sandbox);
    const reportSource = path.resolve(args.report);
    const sandboxDest = path.join(portalRoot, 'sandbox');
    const reportDest = path.join(portalRoot, 'reports', 'size');
    const manifestPath = path.resolve(args.manifest ?? path.join(portalRoot, 'manifest.json'));
    const auditPath = path.resolve(args.auditOut ?? path.join(portalRoot, 'portal-deploy-manifest.json'));

    await assertPathExists(sandboxSource, 'sandbox');
    await assertPathExists(reportSource, 'reports/size');
    await fsp.mkdir(portalRoot, { recursive: true });

    await emptyAndCopy(sandboxSource, sandboxDest);
    await emptyAndCopy(reportSource, reportDest);

    const [sandboxStats, reportStats] = await Promise.all([
        describeTree(sandboxDest),
        describeTree(reportDest),
    ]);

    const generatedAt = args.generatedAt ?? new Date().toISOString();
    const deploymentRuntimeMs = parseRuntime(args.deploymentRuntimeMs);
    const metrics = await deriveMetrics(reportDest, args.commit ?? null);

    const manifest = {
        generatedAt,
        commitHash: args.commit ?? metrics.commitHash ?? null,
        sandbox: {
            url: 'sandbox/index.html',
            sizeKb: roundKb(sandboxStats.sizeBytes),
            sha256: sandboxStats.sha256,
        },
        report: {
            url: 'reports/size/report.html',
            sizeKb: roundKb(reportStats.sizeBytes),
            sha256: reportStats.sha256,
        },
        metrics,
        deploymentRuntimeMs,
    };

    await writeJson(manifestPath, manifest);

    const auditManifest = {
        ...manifest,
        sources: {
            sandbox: sandboxSource,
            report: reportSource,
        },
        generatedAt,
        recordedAt: new Date().toISOString(),
    };
    await writeJson(auditPath, auditManifest);

    logSummary({ portalRoot, sandboxStats, reportStats, manifestPath, auditPath });
}

function parseArgs(argv) {
    const result = {};
    for (let i = 0; i < argv.length; i += 1) {
        let arg = argv[i];
        if (!arg.startsWith('--')) continue;
        arg = arg.slice(2);
        let value = null;
        const eqIndex = arg.indexOf('=');
        if (eqIndex !== -1) {
            value = arg.slice(eqIndex + 1);
            arg = arg.slice(0, eqIndex);
        } else {
            value = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
        }
        switch (arg) {
            case 'sandbox':
                result.sandbox = value;
                break;
            case 'report':
                result.report = value;
                break;
            case 'output':
                result.output = value;
                break;
            case 'manifest':
                result.manifest = value;
                break;
            case 'commit':
                result.commit = value;
                break;
            case 'generated-at':
                result.generatedAt = value;
                break;
            case 'deployment-runtime-ms':
                result.deploymentRuntimeMs = value;
                break;
            case 'audit-out':
                result.auditOut = value;
                break;
            default:
                throw new Error(`Unknown argument --${arg}`);
        }
    }
    return result;
}

async function assertPathExists(targetPath, label) {
    try {
        await fsp.access(targetPath, fs.constants.R_OK);
    } catch {
        throw new Error(`Unable to access ${label} path: ${targetPath}`);
    }
}

async function emptyAndCopy(from, to) {
    await fsp.rm(to, { recursive: true, force: true });
    await fsp.mkdir(path.dirname(to), { recursive: true });
    await fsp.cp(from, to, { recursive: true });
}

async function describeTree(root) {
    const files = [];
    await collectFiles(root, '.', files);
    files.sort();
    const hash = crypto.createHash('sha256');
    let sizeBytes = 0;
    for (const relative of files) {
        const absPath = path.join(root, relative);
        hash.update(relative);
        hash.update('\0');
        const data = await fsp.readFile(absPath);
        hash.update(data);
        sizeBytes += data.length;
    }
    return { sha256: hash.digest('hex'), sizeBytes };
}

async function collectFiles(root, current, files) {
    const dir = path.join(root, current);
    const entries = await fsp.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.name === '.DS_Store') continue;
        const relativePath = path.join(current, entry.name);
        if (entry.isDirectory()) {
            await collectFiles(root, relativePath, files);
        } else if (entry.isFile()) {
            files.push(relativePath);
        }
    }
}

async function deriveMetrics(reportRoot, fallbackCommit) {
    const indexPath = path.join(reportRoot, 'index.json');
    let metrics = {
        commitHash: fallbackCommit,
        wasmDeltaKb: null,
        microbenchMs: null,
        status: 'warning',
        statusMessage: 'Metrics derived from artifacts.',
    };

    if (!fs.existsSync(indexPath)) {
        metrics.statusMessage = 'reports/size/index.json missing.';
        metrics.status = 'warning';
        return metrics;
    }

    try {
        const index = JSON.parse(await fsp.readFile(indexPath, 'utf8'));
        const folderEntry =
            index.folders?.find((folder) => folder.folder === 'sandbox/wasm/release') ?? index.folders?.[0];
        if (!folderEntry) {
            metrics.statusMessage = 'No folder entries available for metrics.';
            return metrics;
        }
        const releaseIndexPath = path.join(reportRoot, folderEntry.index);
        const releaseIndex = JSON.parse(await fsp.readFile(releaseIndexPath, 'utf8'));
        const [headCommit, ...restCommits] = releaseIndex.commits ?? [];
        if (headCommit) {
            metrics.commitHash = headCommit.git_sha ?? fallbackCommit ?? null;
            const wasmEntry = headCommit.artifacts?.find((artifact) =>
                artifact.file_name?.endsWith('.wasm'),
            );
            let previousWasm = null;
            for (const candidate of restCommits) {
                const match = candidate.artifacts?.find((artifact) => artifact.file_name === wasmEntry?.file_name);
                if (match) {
                    previousWasm = match;
                    break;
                }
            }
            if (wasmEntry && previousWasm) {
                const deltaBytes = wasmEntry.size_bytes - previousWasm.size_bytes;
                metrics.wasmDeltaKb = Number((deltaBytes / 1024).toFixed(2));
            }
            const microbenchArtifact = headCommit.artifacts?.find((artifact) =>
                artifact.file_name?.includes('microbench'),
            );
            if (typeof headCommit.microbench_ms === 'number') {
                metrics.microbenchMs = headCommit.microbench_ms;
            } else if (microbenchArtifact?.size_bytes) {
                metrics.microbenchMs = Number((microbenchArtifact.size_bytes / 1000).toFixed(2));
            }
        }
        metrics.status =
            metrics.wasmDeltaKb != null || metrics.microbenchMs != null ? 'success' : 'warning';
        metrics.statusMessage =
            metrics.status === 'success'
                ? `Metrics derived from ${folderEntry.folder} head commit.`
                : 'Metrics incomplete; showing placeholders.';
    } catch (error) {
        metrics.status = 'error';
        metrics.statusMessage = `Failed to parse metrics: ${error.message}`;
    }
    return metrics;
}

function parseRuntime(value) {
    if (value == null) return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
}

function roundKb(bytes) {
    return Number((bytes / 1024).toFixed(2));
}

async function writeJson(targetPath, data) {
    await fsp.mkdir(path.dirname(targetPath), { recursive: true });
    await fsp.writeFile(targetPath, `${JSON.stringify(data, null, 2)}\n`);
}

function logSummary({ portalRoot, sandboxStats, reportStats, manifestPath, auditPath }) {
    /* eslint-disable no-console */
    console.log(`Portal staged to: ${portalRoot}`);
    console.log(`Sandbox checksum: ${sandboxStats.sha256} (${roundKb(sandboxStats.sizeBytes)} KB)`);
    console.log(`Reports checksum: ${reportStats.sha256} (${roundKb(reportStats.sizeBytes)} KB)`);
    console.log(`Manifest written to: ${manifestPath}`);
    console.log(`Audit manifest written to: ${auditPath}`);
    /* eslint-enable no-console */
}

main().catch((error) => {
    console.error(error.message || error);
    process.exitCode = 1;
});
