#!/usr/bin/env node
/**
 * Local stdio MCP server for Agentic System (offline, zero login, zero dependencies).
 *
 * Usage:
 *   node apps/mcp/stdio.mjs
 */

import { createInterface } from 'node:readline';
import { handleJsonRpcMessage } from './core.mjs';

const rl = createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
});

rl.on('line', (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;

  let parsed;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    process.stdout.write(
      `${JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        error: { code: -32700, message: 'Parse error' },
      })}\n`,
    );
    return;
  }

  if (Array.isArray(parsed)) {
    const responses = parsed
      .map((item) => handleJsonRpcMessage(item))
      .filter((item) => item !== null);
    if (responses.length > 0) {
      process.stdout.write(`${JSON.stringify(responses)}\n`);
    }
    return;
  }

  const response = handleJsonRpcMessage(parsed);
  if (response !== null) {
    process.stdout.write(`${JSON.stringify(response)}\n`);
  }
});
