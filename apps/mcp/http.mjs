#!/usr/bin/env node
/**
 * Local Streamable HTTP runner for the Agentic System MCP server.
 *
 * Usage:
 *   node apps/mcp/http.mjs
 *   PORT=8788 HOST=127.0.0.1 node apps/mcp/http.mjs
 */

import { createServer } from 'node:http';
import { handleHttpRequest } from './core.mjs';

export function startHttpServer({ host = '127.0.0.1', port = 8788 } = {}) {
  const server = createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const body = chunks.length > 0 ? Buffer.concat(chunks) : undefined;
    const url = `http://${req.headers.host || `${host}:${port}`}${req.url || '/'}`;

    const request = new Request(url, {
      method: req.method,
      headers: req.headers,
      body: req.method === 'GET' || req.method === 'HEAD' ? undefined : body,
    });

    const response = await handleHttpRequest(request);
    res.statusCode = response.status;
    response.headers.forEach((value, key) => {
      res.setHeader(key, value);
    });
    const out = Buffer.from(await response.arrayBuffer());
    res.end(out);
  });

  return new Promise((resolvePromise) => {
    server.listen(port, host, () => {
      const address = server.address();
      resolvePromise({ server, host: address.address, port: address.port });
    });
  });
}

if (process.argv[1] && process.argv[1].endsWith('http.mjs')) {
  const host = process.env.HOST || '127.0.0.1';
  const port = Number(process.env.PORT || 8788);
  startHttpServer({ host, port }).then(({ host: boundHost, port: boundPort }) => {
    console.log(`Agentic System MCP server listening at http://${boundHost}:${boundPort}/mcp`);
  });
}
