// Minimal, dependency-free HTTP wrapper around a headless Blender
// invocation. Deliberately NOT a NestJS/Express app — this service does
// exactly one thing (run 3d/generate_flag.py against 3d/flag.blend and
// return the PNG), so a raw node:http server keeps its own footprint (and
// the Docker image built around it) as small as the Blender dependency
// itself allows. See pergolando-backend's Scene3dService for the caller;
// see 3d/NOTES.md for what generate_flag.py actually does.

import { execFile } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

const PORT = Number(process.env.PORT ?? 8080);
const BLENDER_EXECUTABLE_PATH = process.env.BLENDER_EXECUTABLE_PATH;
const THREED_ASSETS_PATH = process.env.THREED_ASSETS_PATH;
const BLENDER_TIMEOUT_MS = 90_000;
const MAX_BODY_BYTES = 1_000_000; // the request is just numbers, this is generous

if (!BLENDER_EXECUTABLE_PATH || !THREED_ASSETS_PATH) {
  console.error(
    'BLENDER_EXECUTABLE_PATH and THREED_ASSETS_PATH must both be set — refusing to start.',
  );
  process.exit(1);
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error('payload-too-large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch {
        reject(new Error('invalid-json'));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

/**
 * The request body IS the `generate_flag.py` config object as-is (L_cm,
 * P_cm, H_cm, deltaH_cm, fissaggio, optional camera{...}/outputMode) — this
 * service doesn't know or care about the catalog/wizard's own field names,
 * that mapping lives in pergolando-backend's Scene3dService.
 */
async function handleRender3d(req, res) {
  let config;
  try {
    config = await readJsonBody(req);
  } catch (err) {
    sendJson(res, 400, { error: err.message === 'payload-too-large' ? err.message : 'invalid-json' });
    return;
  }

  const flagBlendPath = join(THREED_ASSETS_PATH, 'flag.blend');
  const scriptPath = join(THREED_ASSETS_PATH, 'generate_flag.py');
  const tmpDir = await mkdtemp(join(tmpdir(), 'pergolando-render-'));
  const outputPath = join(tmpDir, `${randomUUID()}.png`);

  try {
    await execFileAsync(
      BLENDER_EXECUTABLE_PATH,
      [
        '--background',
        // Skips the user's own addons/preferences for this one headless
        // invocation (factory defaults only) — without it, every single
        // render in this session loaded two unrelated third-party addons:
        // "bonsai" (a BIM/IFC addon, Python-version-incompatible with this
        // Blender build, printing a RuntimeError on every launch) and
        // BlenderKit (an asset-library addon that spawns its own separate
        // client process on startup). Neither has any business in a
        // scripted render service; found while diagnosing a real Blender
        // crash ("bad allocation" loading OpenColorIO) that coincided with
        // a leftover BlenderKit client process still running from an
        // earlier failed render — see 3d/NOTES.md.
        '--factory-startup',
        flagBlendPath,
        '--python',
        scriptPath,
        '--',
        '--config-json',
        JSON.stringify(config),
        '--output',
        outputPath,
      ],
      { timeout: BLENDER_TIMEOUT_MS },
    );
  } catch (err) {
    console.error('Blender invocation failed:', err);
    await rm(tmpDir, { recursive: true, force: true });
    sendJson(res, 502, { error: 'render-failed' });
    return;
  }

  try {
    const buffer = await readFile(outputPath);
    sendJson(res, 200, { imageBase64: buffer.toString('base64'), mimeType: 'image/png' });
  } catch (err) {
    console.error('Blender produced no output file:', err);
    sendJson(res, 502, { error: 'render-failed' });
  } finally {
    await rm(tmpDir, { recursive: true, force: true });
  }
}

const server = createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    sendJson(res, 200, { status: 'ok' });
    return;
  }
  if (req.method === 'POST' && req.url === '/render3d') {
    handleRender3d(req, res).catch((err) => {
      console.error('Unexpected error handling /render3d:', err);
      sendJson(res, 500, { error: 'internal-error' });
    });
    return;
  }
  sendJson(res, 404, { error: 'not-found' });
});

server.listen(PORT, () => {
  console.log(`pergolando-blender-service listening on :${PORT}`);
});
