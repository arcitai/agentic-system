#!/usr/bin/env node
/**
 * Build the deterministic, zero-dependency Agentic System bundle for apps/mcp.
 *
 * Reads only reviewed repository method files (foundation/, entry/,
 * evaluation/, defence/, templates/project-brief.md, README.md, VISION.md,
 * docs/*.md, VERSION) and writes bundle.generated.mjs with per-file SHA-256
 * digests. No network calls, no customer data, no credentials.
 */

import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, posix, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '..', '..');
const OUTPUT_PATH = resolve(HERE, 'bundle.generated.mjs');

const SKILL_GROUPS = ['foundation', 'entry', 'evaluation', 'defence'];
const ALLOWED_EXTENSIONS = new Set(['.md', '.json', '.yaml', '.yml']);
const REPOSITORY_URL = 'https://github.com/arcitai/agentic-system';
const NOTION_GUIDE_URL = 'https://gustavanderson.notion.site/Agentic-System-4046d2e17f568159a603de2dd6b91c2a';

function sha256(text) {
  return createHash('sha256').update(text, 'utf8').digest('hex');
}

function walkSorted(dir) {
  const results = [];
  for (const entry of readdirSync(dir).sort()) {
    const full = resolve(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      results.push(...walkSorted(full));
    } else if (stat.isFile()) {
      const ext = entry.includes('.') ? entry.slice(entry.lastIndexOf('.')) : '';
      if (ALLOWED_EXTENSIONS.has(ext)) {
        results.push(full);
      }
    }
  }
  return results;
}

function unquote(raw) {
  const trimmed = raw.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return JSON.parse(trimmed);
  }
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return trimmed.slice(1, -1).replace(/''/g, "'");
  }
  return trimmed;
}

function parseSkillFrontmatter(text, relPath) {
  if (!text.startsWith('---\n') || !text.includes('\n---\n', 4)) {
    throw new Error(`Missing YAML frontmatter in ${relPath}`);
  }
  const header = text.slice(4, text.indexOf('\n---\n', 4));
  let name = '';
  let description = '';
  let license = '';
  let version = '';
  let updated = '';
  for (const line of header.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const nameMatch = line.match(/^name:\s*(.+)$/);
    if (nameMatch) {
      name = unquote(nameMatch[1]);
      continue;
    }
    const descMatch = line.match(/^description:\s*(.+)$/);
    if (descMatch) {
      description = unquote(descMatch[1]);
      continue;
    }
    const licMatch = line.match(/^license:\s*(.+)$/);
    if (licMatch) {
      license = unquote(licMatch[1]);
      continue;
    }
    const verMatch = line.match(/^  version:\s*(.+)$/);
    if (verMatch) {
      version = unquote(verMatch[1]);
      continue;
    }
    const updMatch = line.match(/^  updated:\s*(.+)$/);
    if (updMatch) {
      updated = unquote(updMatch[1]);
    }
  }
  if (!name || !description || !version) {
    throw new Error(`Incomplete skill frontmatter in ${relPath}`);
  }
  return { name, description, license: license || 'MIT', version, updated };
}

export function buildBundle(repoRoot = REPO_ROOT) {
  const version = readFileSync(resolve(repoRoot, 'VERSION'), 'utf8').trim();
  const files = {};

  const addFile = (fullPath) => {
    const rel = relative(repoRoot, fullPath).split('\\').join(posix.sep);
    const content = readFileSync(fullPath, 'utf8');
    files[rel] = {
      sha256: sha256(content),
      bytes: Buffer.byteLength(content, 'utf8'),
      content,
    };
    return rel;
  };

  for (const topFile of ['README.md', 'VISION.md', 'templates/project-brief.md']) {
    const full = resolve(repoRoot, topFile);
    if (existsSync(full)) addFile(full);
  }

  const docsDir = resolve(repoRoot, 'docs');
  if (existsSync(docsDir)) {
    for (const entry of readdirSync(docsDir).sort()) {
      const full = resolve(docsDir, entry);
      if (statSync(full).isFile() && entry.endsWith('.md')) {
        addFile(full);
      }
    }
  }

  const methods = [];
  for (const group of SKILL_GROUPS) {
    const groupDir = resolve(repoRoot, group);
    if (!existsSync(groupDir)) continue;
    for (const entry of readdirSync(groupDir).sort()) {
      const skillDir = resolve(groupDir, entry);
      if (!statSync(skillDir).isDirectory()) continue;
      const skillFile = resolve(skillDir, 'SKILL.md');
      if (!existsSync(skillFile)) continue;

      for (const filePath of walkSorted(skillDir)) {
        addFile(filePath);
      }

      const skillRel = `${group}/${entry}/SKILL.md`;
      const folderPrefix = `${group}/${entry}/`;
      const supporting = Object.keys(files)
        .filter((key) => key.startsWith(folderPrefix) && key !== skillRel)
        .sort();

      const meta = parseSkillFrontmatter(files[skillRel].content, skillRel);
      methods.push({
        name: meta.name,
        group,
        description: meta.description,
        version: meta.version,
        updated: meta.updated,
        license: meta.license,
        path: skillRel,
        sha256: files[skillRel].sha256,
        bytes: files[skillRel].bytes,
        references: supporting,
      });
    }
  }

  const orderedFileKeys = Object.keys(files).sort();
  const orderedFiles = {};
  for (const key of orderedFileKeys) {
    orderedFiles[key] = files[key];
  }

  const manifestDigestInput = orderedFileKeys
    .map((key) => `${key}:${orderedFiles[key].sha256}`)
    .join('\n');

  const releaseTag = `v${version}`;

  return {
    name: 'agentic-systems-mcp',
    version,
    release_tag: releaseTag,
    description: 'Open framework with guidance, reusable methods and project templates for building and operating agentic systems.',
    license: 'MIT',
    repository: REPOSITORY_URL,
    release_url: `${REPOSITORY_URL}/releases/tag/${releaseTag}`,
    notion_guide_url: NOTION_GUIDE_URL,
    bundle_sha256: sha256(manifestDigestInput),
    method_count: methods.length,
    file_count: orderedFileKeys.length,
    methods,
    files: orderedFiles,
  };
}

export function renderBundleSource(bundle) {
  return (
    '// Generated by apps/mcp/build.mjs from reviewed repository method files.\n' +
    '// Do not edit by hand. Re-run: node apps/mcp/build.mjs\n' +
    `export const AGENTIC_SYSTEM_BUNDLE = ${JSON.stringify(bundle, null, 2)};\n`
  );
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const bundle = buildBundle();
  writeFileSync(OUTPUT_PATH, renderBundleSource(bundle), 'utf8');
  console.log(
    `Built apps/mcp/bundle.generated.mjs (Agentic System ${bundle.version}, ` +
      `${bundle.method_count} methods, ${bundle.file_count} files, sha256=${bundle.bundle_sha256.slice(0, 12)})`,
  );
}
