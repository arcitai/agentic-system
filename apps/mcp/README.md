# Agentic System MCP Server

Revision: 0.2.3 · Updated: 2026-11-26

Public, stateless, read-only, login-free MCP server for [Agentic System](../../README.md).

## Endpoints

- Latest release: `https://mcp-agentic-systems.arcitai.com/mcp`
- Pinned release: `https://mcp-agentic-systems.arcitai.com/v0.2.3/mcp`
- Health and SHA-256 verification: `https://mcp-agentic-systems.arcitai.com/health`

## Privacy and safety

- No login, no API keys, no cookies. Requests carrying `Authorization` or `Cookie` headers are rejected with HTTP 400.
- Stateless and read-only. Serves only the reviewed public framework methods, templates, and documentation bundled from GitHub.
- Zero request logging (`observability.enabled = false`) and zero customer data storage.

## Build, test, and run locally

```sh
node apps/mcp/build.mjs
node --test apps/mcp/mcp.test.mjs
node apps/mcp/stdio.mjs
node apps/mcp/http.mjs
```

## Deploy to Cloudflare Workers

```sh
cd apps/mcp
npx wrangler deploy
```
