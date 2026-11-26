/**
 * Cloudflare Worker entrypoint for the public, stateless, login-free Agentic System MCP server.
 */

import { handleHttpRequest } from './core.mjs';

export default {
  async fetch(request) {
    return handleHttpRequest(request);
  },
};
