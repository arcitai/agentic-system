/**
 * Core stateless, zero-login MCP JSON-RPC 2.0 handler for Agentic System.
 *
 * Privacy and security guarantees:
 * - Read-only, public framework methods and docs only (bundled from reviewed GitHub releases).
 * - Zero authentication, zero cookies, zero tokens, zero user data.
 * - Never logs request bodies or caller metadata.
 * - Never calls external networks or accesses local files at runtime.
 */

import { AGENTIC_SYSTEM_BUNDLE } from './bundle.generated.mjs';

export const SUPPORTED_PROTOCOL_VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05'];

export const PRIVACY_POLICY = Object.freeze({
  auth: 'none',
  stateless: true,
  read_only: true,
  logs_user_data: false,
  stores_customer_data: false,
});

export const SERVER_INSTRUCTIONS =
  'Public, read-only, login-free MCP server for Agentic System (github.com/arcitai/agentic-system). ' +
  'Call agentic_list_methods to see the portable framework methods (compact summary) before loading a full method with agentic_get_method. ' +
  'Call agentic_get_project_brief to inspect the optional project brief starter template. ' +
  'Call agentic_get_reference to read one specific supporting reference or documentation file (such as README.md, VISION.md, or docs/architecture.md). ' +
  'This server works across Codex, Claude Code, T3 Code, OpenBot, Grok Bot, and any MCP client. ' +
  'It never authenticates, never stores or logs user data, and never modifies project files or external services.';

const TOOL_DEFINITIONS = [
  {
    name: 'agentic_list_methods',
    description:
      'List all bundled Agentic System portable methods (name, group, short description, version, sha256) and documentation paths without loading full method bodies.',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {},
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  {
    name: 'agentic_get_method',
    description:
      'Return the full SKILL.md instructions, version, SHA-256 digest, and supporting reference paths for one Agentic System method by exact name (for example agentic-foundation, agentic-entry, agentic-evaluate, agentic-security).',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      required: ['name'],
      properties: {
        name: {
          type: 'string',
          description: 'Exact Agentic System method name, such as agentic-foundation.',
        },
      },
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  {
    name: 'agentic_get_project_brief',
    description:
      'Return the optional Agentic System project brief template (templates/project-brief.md) for defining a project outcome, trusted sources, authority, and checks.',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {},
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  {
    name: 'agentic_get_reference',
    description:
      'Return one bundled Agentic System reference, guide, or template by exact relative repository path (for example README.md, VISION.md, docs/architecture.md, or a method reference path).',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      required: ['path'],
      properties: {
        path: {
          type: 'string',
          description: 'Exact relative path inside the Agentic System bundle, such as docs/architecture.md.',
        },
      },
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  {
    name: 'agentic_version',
    description:
      'Return the Agentic System package version, GitHub release URL, bundle SHA-256 checksum, Notion guide URL, and stateless/no-login privacy guarantee.',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {},
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
];

function jsonRpcResult(id, result) {
  return { jsonrpc: '2.0', id, result };
}

function jsonRpcError(id, code, message, data) {
  const error = { code, message };
  if (data !== undefined) error.data = data;
  return { jsonrpc: '2.0', id: id ?? null, error };
}

function toolText(text, structuredContent, isError = false) {
  const payload = {
    content: [{ type: 'text', text }],
  };
  if (structuredContent !== undefined) {
    payload.structuredContent = structuredContent;
  }
  if (isError) {
    payload.isError = true;
  }
  return payload;
}

function mimeTypeFor(path) {
  if (path.endsWith('.json')) return 'application/json';
  if (path.endsWith('.yaml') || path.endsWith('.yml')) return 'application/yaml';
  return 'text/markdown';
}

function executeTool(name, args = {}, bundle = AGENTIC_SYSTEM_BUNDLE) {
  if (args !== null && (typeof args !== 'object' || Array.isArray(args))) {
    return toolText('Tool arguments must be a JSON object.', undefined, true);
  }
  const safeArgs = args ?? {};

  switch (name) {
    case 'agentic_list_methods': {
      const docs = Object.keys(bundle.files)
        .filter((key) => key === 'README.md' || key === 'VISION.md' || key.startsWith('docs/') || key.startsWith('templates/'))
        .sort();
      const summary = {
        package: bundle.name,
        version: bundle.version,
        release_tag: bundle.release_tag,
        release_url: bundle.release_url,
        notion_guide_url: bundle.notion_guide_url,
        bundle_sha256: bundle.bundle_sha256,
        methods: bundle.methods.map((method) => ({
          name: method.name,
          group: method.group,
          version: method.version,
          updated: method.updated,
          description: method.description,
          sha256: method.sha256,
          reference_count: method.references.length,
        })),
        docs,
        privacy: PRIVACY_POLICY,
      };
      return toolText(JSON.stringify(summary, null, 2), summary);
    }

    case 'agentic_get_method': {
      const methodName = typeof safeArgs.name === 'string' ? safeArgs.name.trim() : '';
      if (!methodName) {
        return toolText(
          `Missing required "name". Valid methods: ${bundle.methods.map((m) => m.name).join(', ')}`,
          undefined,
          true,
        );
      }
      const method = bundle.methods.find((entry) => entry.name === methodName);
      if (!method) {
        return toolText(
          `Unknown Agentic System method "${methodName}". Valid methods: ${bundle.methods.map((m) => m.name).join(', ')}`,
          undefined,
          true,
        );
      }
      const file = bundle.files[method.path];
      const header = [
        `<!-- Agentic System ${bundle.version} | ${method.name} ${method.version} | ${method.path} | sha256:${method.sha256} -->`,
        method.references.length > 0
          ? `<!-- Supporting references (read with agentic_get_reference): ${method.references.join(', ')} -->`
          : '<!-- Supporting references: none -->',
        '',
        file.content.trimEnd(),
      ].join('\n');

      return toolText(header, {
        package_version: bundle.version,
        name: method.name,
        group: method.group,
        version: method.version,
        updated: method.updated,
        path: method.path,
        sha256: method.sha256,
        references: method.references,
      });
    }

    case 'agentic_get_project_brief': {
      const briefPath = 'templates/project-brief.md';
      const file = bundle.files[briefPath];
      if (!file) {
        return toolText(`Template not found in bundle: ${briefPath}`, undefined, true);
      }
      const text = [
        `<!-- Agentic System ${bundle.version} | ${briefPath} | sha256:${file.sha256} -->`,
        '',
        file.content.trimEnd(),
      ].join('\n');
      return toolText(text, {
        package_version: bundle.version,
        path: briefPath,
        sha256: file.sha256,
        bytes: file.bytes,
      });
    }

    case 'agentic_get_reference': {
      const requestedPath = typeof safeArgs.path === 'string' ? safeArgs.path.trim() : '';
      if (!requestedPath) {
        return toolText(
          'Missing required "path" (for example "README.md", "docs/architecture.md", or "templates/project-brief.md").',
          undefined,
          true,
        );
      }
      if (!Object.prototype.hasOwnProperty.call(bundle.files, requestedPath)) {
        return toolText(
          `Reference not found in Agentic System ${bundle.version} bundle: "${requestedPath}". ` +
            'Call agentic_list_methods or agentic_get_method to inspect valid relative paths.',
          undefined,
          true,
        );
      }
      const file = bundle.files[requestedPath];
      const text = [
        `<!-- Agentic System ${bundle.version} | ${requestedPath} | sha256:${file.sha256} -->`,
        '',
        file.content.trimEnd(),
      ].join('\n');

      return toolText(text, {
        package_version: bundle.version,
        path: requestedPath,
        sha256: file.sha256,
        bytes: file.bytes,
      });
    }

    case 'agentic_version': {
      const info = {
        name: bundle.name,
        version: bundle.version,
        release_tag: bundle.release_tag,
        repository: bundle.repository,
        release_url: bundle.release_url,
        notion_guide_url: bundle.notion_guide_url,
        license: bundle.license,
        bundle_sha256: bundle.bundle_sha256,
        method_count: bundle.method_count,
        file_count: bundle.file_count,
        privacy: PRIVACY_POLICY,
      };
      return toolText(JSON.stringify(info, null, 2), info);
    }

    default:
      return null;
  }
}

function listResources(bundle = AGENTIC_SYSTEM_BUNDLE) {
  const resources = [];
  if (bundle.files['README.md']) {
    resources.push({
      uri: 'agentic://overview',
      name: 'Agentic System Overview (README.md)',
      description: `Overview for Agentic System ${bundle.version}.`,
      mimeType: 'text/markdown',
    });
  }
  if (bundle.files['templates/project-brief.md']) {
    resources.push({
      uri: 'agentic://project-brief',
      name: 'Project Brief Template',
      description: 'Optional project brief template for defining outcomes, sources, authority, and checks.',
      mimeType: 'text/markdown',
    });
  }
  for (const method of bundle.methods) {
    resources.push({
      uri: `agentic://method/${method.name}`,
      name: `${method.name} (${method.version})`,
      description: method.description,
      mimeType: 'text/markdown',
    });
  }
  for (const filePath of Object.keys(bundle.files)) {
    if (filePath === 'README.md' || filePath === 'templates/project-brief.md' || filePath.endsWith('/SKILL.md')) {
      continue;
    }
    resources.push({
      uri: `agentic://ref/${filePath}`,
      name: filePath,
      description: `Bundled Agentic System ${bundle.version} reference file.`,
      mimeType: mimeTypeFor(filePath),
    });
  }
  return resources;
}

function readResource(uri, bundle = AGENTIC_SYSTEM_BUNDLE) {
  if (typeof uri !== 'string') return null;
  if (uri === 'agentic://overview' && bundle.files['README.md']) {
    return { uri, mimeType: 'text/markdown', text: bundle.files['README.md'].content };
  }
  if (uri === 'agentic://project-brief' && bundle.files['templates/project-brief.md']) {
    return { uri, mimeType: 'text/markdown', text: bundle.files['templates/project-brief.md'].content };
  }
  if (uri.startsWith('agentic://method/')) {
    const methodName = uri.slice('agentic://method/'.length);
    const method = bundle.methods.find((entry) => entry.name === methodName);
    if (!method) return null;
    return { uri, mimeType: 'text/markdown', text: bundle.files[method.path].content };
  }
  if (uri.startsWith('agentic://ref/')) {
    const relPath = uri.slice('agentic://ref/'.length);
    if (!Object.prototype.hasOwnProperty.call(bundle.files, relPath)) return null;
    return { uri, mimeType: mimeTypeFor(relPath), text: bundle.files[relPath].content };
  }
  return null;
}

export function handleJsonRpcMessage(message, bundle = AGENTIC_SYSTEM_BUNDLE) {
  if (!message || typeof message !== 'object' || Array.isArray(message)) {
    return jsonRpcError(null, -32600, 'Invalid Request');
  }
  if (message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
    return jsonRpcError(message.id ?? null, -32600, 'Invalid JSON-RPC 2.0 request');
  }

  const isNotification = message.id === undefined;
  const { id, method, params } = message;

  if (method === 'notifications/initialized' || method === 'notifications/cancelled') {
    return null;
  }

  if (method === 'initialize') {
    const requestedVersion =
      params && typeof params.protocolVersion === 'string' ? params.protocolVersion : null;
    const protocolVersion =
      requestedVersion && SUPPORTED_PROTOCOL_VERSIONS.includes(requestedVersion)
        ? requestedVersion
        : SUPPORTED_PROTOCOL_VERSIONS[0];

    return jsonRpcResult(id, {
      protocolVersion,
      capabilities: {
        tools: { listChanged: false },
        resources: { subscribe: false, listChanged: false },
        prompts: { listChanged: false },
      },
      serverInfo: {
        name: 'agentic-systems-mcp',
        title: 'Agentic System',
        version: bundle.version,
      },
      instructions: SERVER_INSTRUCTIONS,
    });
  }

  if (method === 'ping') {
    return jsonRpcResult(id, {});
  }

  if (method === 'tools/list') {
    return jsonRpcResult(id, { tools: TOOL_DEFINITIONS });
  }

  if (method === 'tools/call') {
    const toolName = params && typeof params.name === 'string' ? params.name : '';
    const toolArgs = params && params.arguments !== undefined ? params.arguments : {};
    const result = executeTool(toolName, toolArgs, bundle);
    if (result === null) {
      return jsonRpcError(id, -32602, `Unknown tool: ${toolName}`);
    }
    return jsonRpcResult(id, result);
  }

  if (method === 'resources/list') {
    return jsonRpcResult(id, { resources: listResources(bundle) });
  }

  if (method === 'resources/read') {
    const uri = params && typeof params.uri === 'string' ? params.uri : '';
    const resource = readResource(uri, bundle);
    if (!resource) {
      return jsonRpcError(id, -32002, `Resource not found: ${uri}`);
    }
    return jsonRpcResult(id, { contents: [resource] });
  }

  if (method === 'prompts/list') {
    return jsonRpcResult(id, {
      prompts: [
        {
          name: 'agentic-foundation',
          description: 'Prepare, assess, or maintain a project working ground using Agentic Foundation.',
          arguments: [],
        },
      ],
    });
  }

  if (method === 'prompts/get') {
    const promptName = params && typeof params.name === 'string' ? params.name : '';
    if (promptName !== 'agentic-foundation') {
      return jsonRpcError(id, -32602, `Unknown prompt: ${promptName}`);
    }
    const foundationFile = bundle.files['foundation/agentic-foundation/SKILL.md'];
    return jsonRpcResult(id, {
      description: 'Official Agentic Foundation method.',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text:
              `Follow the Agentic Foundation method from Agentic System ${bundle.version} below:\n\n` +
              foundationFile.content,
          },
        },
      ],
    });
  }

  if (isNotification) {
    return null;
  }

  return jsonRpcError(id, -32601, `Method not found: ${method}`);
}

const CORS_HEADERS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET, POST, OPTIONS',
  'access-control-allow-headers': 'Content-Type, Accept, MCP-Protocol-Version',
  'cache-control': 'no-store',
  'x-content-type-options': 'nosniff',
};

function jsonResponse(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...CORS_HEADERS,
      ...extraHeaders,
    },
  });
}

export async function handleHttpRequest(request, bundle = AGENTIC_SYSTEM_BUNDLE) {
  const url = new URL(request.url);
  const { pathname } = url;

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  if (request.headers.get('authorization') || request.headers.get('cookie')) {
    return jsonResponse(
      {
        error: 'credentials_not_accepted',
        message:
          'Agentic System MCP is public, stateless, and login-free. Do not send Authorization headers, API tokens, or cookies.',
      },
      400,
    );
  }

  if ((pathname === '/' || pathname === '/health') && request.method === 'GET') {
    return jsonResponse({
      name: 'agentic-systems-mcp',
      package: bundle.name,
      version: bundle.version,
      release_tag: bundle.release_tag,
      release_url: bundle.release_url,
      repository: bundle.repository,
      notion_guide_url: bundle.notion_guide_url,
      bundle_sha256: bundle.bundle_sha256,
      method_count: bundle.method_count,
      file_count: bundle.file_count,
      endpoints: {
        mcp: '/mcp',
        pinned_mcp: `/v${bundle.version}/mcp`,
        health: '/health',
      },
      privacy: PRIVACY_POLICY,
    });
  }

  const versionedMatch = pathname.match(/^\/v(\d+\.\d+\.\d+)\/mcp$/);
  if (versionedMatch && versionedMatch[1] !== bundle.version) {
    return jsonResponse(
      {
        error: 'version_not_served',
        requested_version: versionedMatch[1],
        served_version: bundle.version,
        pinned_endpoint: `/v${bundle.version}/mcp`,
        release_url: bundle.release_url,
      },
      404,
    );
  }

  const isMcpRoute = pathname === '/mcp' || Boolean(versionedMatch);
  if (!isMcpRoute) {
    return jsonResponse({ error: 'not_found' }, 404);
  }

  if (request.method !== 'POST') {
    return new Response(null, {
      status: 405,
      headers: {
        ...CORS_HEADERS,
        allow: 'POST, OPTIONS',
      },
    });
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return jsonResponse(jsonRpcError(null, -32700, 'Parse error: expected valid JSON'), 400);
  }

  if (Array.isArray(payload)) {
    if (payload.length === 0) {
      return jsonResponse(jsonRpcError(null, -32600, 'Invalid Request: empty batch'), 400);
    }
    const responses = payload
      .map((item) => handleJsonRpcMessage(item, bundle))
      .filter((item) => item !== null);
    if (responses.length === 0) {
      return new Response(null, { status: 202, headers: CORS_HEADERS });
    }
    return jsonResponse(responses, 200);
  }

  const response = handleJsonRpcMessage(payload, bundle);
  if (response === null) {
    return new Response(null, { status: 202, headers: CORS_HEADERS });
  }
  return jsonResponse(response, 200);
}
