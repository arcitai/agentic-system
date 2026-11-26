import assert from 'node:assert/strict';
import test from 'node:test';
import { buildBundle } from './build.mjs';
import { AGENTIC_SYSTEM_BUNDLE } from './bundle.generated.mjs';
import { handleHttpRequest, handleJsonRpcMessage } from './core.mjs';

test('generated bundle matches current repository files and hashes', () => {
  const fresh = buildBundle();
  assert.equal(AGENTIC_SYSTEM_BUNDLE.version, fresh.version);
  assert.equal(AGENTIC_SYSTEM_BUNDLE.bundle_sha256, fresh.bundle_sha256);
  assert.equal(AGENTIC_SYSTEM_BUNDLE.method_count, 4);
  assert.deepEqual(
    AGENTIC_SYSTEM_BUNDLE.methods.map((m) => m.name),
    ['agentic-foundation', 'agentic-entry', 'agentic-evaluate', 'agentic-security'],
  );
});

test('initialize, tools/list, and tools/call work cleanly', () => {
  const init = handleJsonRpcMessage({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { protocolVersion: '2025-06-18' },
  });
  assert.equal(init.result.serverInfo.name, 'agentic-systems-mcp');
  assert.equal(init.result.serverInfo.version, AGENTIC_SYSTEM_BUNDLE.version);

  const listed = handleJsonRpcMessage({ jsonrpc: '2.0', id: 2, method: 'tools/list' });
  assert.deepEqual(
    listed.result.tools.map((t) => t.name),
    [
      'agentic_list_methods',
      'agentic_get_method',
      'agentic_get_project_brief',
      'agentic_get_reference',
      'agentic_version',
    ],
  );

  const method = handleJsonRpcMessage({
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: { name: 'agentic_get_method', arguments: { name: 'agentic-foundation' } },
  });
  assert.equal(method.result.isError, undefined);
  assert.match(method.result.content[0].text, /agentic-foundation/);

  const brief = handleJsonRpcMessage({
    jsonrpc: '2.0',
    id: 4,
    method: 'tools/call',
    params: { name: 'agentic_get_project_brief', arguments: {} },
  });
  assert.equal(brief.result.isError, undefined);
  assert.match(brief.result.content[0].text, /Project brief/i);

  const traversal = handleJsonRpcMessage({
    jsonrpc: '2.0',
    id: 5,
    method: 'tools/call',
    params: { name: 'agentic_get_reference', arguments: { path: '../../etc/passwd' } },
  });
  assert.equal(traversal.result.isError, true);
});

test('HTTP handler exposes health, /mcp, pinned /vX.Y.Z/mcp, and rejects credentials', async () => {
  const healthRes = await handleHttpRequest(new Request('https://mcp-agentic-systems.arcitai.com/health'));
  assert.equal(healthRes.status, 200);
  const health = await healthRes.json();
  assert.equal(health.version, AGENTIC_SYSTEM_BUNDLE.version);
  assert.equal(health.privacy.auth, 'none');

  const authRes = await handleHttpRequest(
    new Request('https://mcp-agentic-systems.arcitai.com/mcp', {
      method: 'POST',
      headers: { authorization: 'Bearer secret', 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'ping' }),
    }),
  );
  assert.equal(authRes.status, 400);

  const pinnedRes = await handleHttpRequest(
    new Request(`https://mcp-agentic-systems.arcitai.com/v${AGENTIC_SYSTEM_BUNDLE.version}/mcp`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'ping' }),
    }),
  );
  assert.equal(pinnedRes.status, 200);
  assert.deepEqual(await pinnedRes.json(), { jsonrpc: '2.0', id: 1, result: {} });
});
