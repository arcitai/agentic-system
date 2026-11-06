# Migrate an optional method package on a host

Revision: 0.1.22 · Updated: 2026-10-23

Agentic Systems depends on no personal-method package. Some owners also use one, such as
**The Onlinesourdough Method (OSM)**, formerly AIOS. When that package changes its
identity, the hosts and consumers that call it must move without breaking working
calls or the owner's context. This guide covers that host and consumer side. The
package's own repository owns its source, release and distribution.

## OSM status, as of 2026-10-23

- The public name is The Onlinesourdough Method (OSM). "Context Architecture" is a
  descriptive term, not a product. The owner's instruction page, **AI Operating
  Model**, keeps its name, link, selected home and IDs.
- The canonical repository is
  [onlinesourdough/OSM-plugin](https://github.com/onlinesourdough/OSM-plugin). Its
  plugin is `osm`, selected as `osm@online-sourdough` in Codex and Claude; the
  marketplace publisher `online-sourdough` is unchanged. The core skills are
  `osm` and `osm-*`, while `content` and `diffusion-studio` keep their unprefixed
  names.
- Public metadata read on 2026-10-23:
  [v0.30.0](https://github.com/onlinesourdough/OSM-plugin/releases/tag/v0.30.0) is a
  **prerelease**, not a stable release. Its tag is the merge commit
  `314dcf17a06014df472a32cdb10f847672cba0be` of
  [PR #80](https://github.com/onlinesourdough/OSM-plugin/pull/80). Package CI
  passed on that pull request's head commit, not on the tag commit itself.
- The package lane ([OSM #62](https://github.com/onlinesourdough/OSM-plugin/issues/62)),
  the distribution lane ([OSM #77](https://github.com/onlinesourdough/OSM-plugin/issues/77))
  and the parent ledger ([OSM #76](https://github.com/onlinesourdough/OSM-plugin/issues/76))
  remain with their own owners. Host and consumer preparation is
  [Agentic Systems #93](https://github.com/arcitai/agentic-systems/issues/93).

Publication is not use. A release migrates no host, and the metadata above shows
no host or caller using it. On each host, keep the working AIOS 0.29 callers,
selectors and existing reviewed installation until that host has its own exact
compatible candidate, owner authority, idle checkpoint with a current quiet
recovery copy, fresh-session discovery, invocation and use, and a qualified
rollback. Do not silently replace an installed reviewed preview, such as a Setup
preview, with the base release; a separately versioned preview needs its own
qualification and selection.

Take harness-specific steps from the candidate's own pinned
[native installation](https://github.com/onlinesourdough/OSM-plugin/blob/314dcf17a06014df472a32cdb10f847672cba0be/docs/native-installation.md)
and [migration](https://github.com/onlinesourdough/OSM-plugin/blob/314dcf17a06014df472a32cdb10f847672cba0be/skills/osm-setup/references/migration.md)
documents; this guide does not repeat their commands. A fixed-version install names
an existing reviewed, immutable ref. The unpinned route in the README follows the
`main` branch, so it is not a qualified fixed version.

## Classify before changing

Sort every occurrence into one class:

| Class | Examples | Rule |
| --- | --- | --- |
| Current branding | Display names and current descriptions in guidance | Update to the current name |
| Executable identifier | Invocation and skill names, plugin IDs, marketplace selectors, install URLs, MCP identifiers | Change only together with the qualified package and its real callers |
| Compatibility or storage | Managed markers such as `AIOS:BEGIN`, source keys, context page and database IDs | Keep, and document why |
| History | Release notes, past evidence, provenance and license attribution, original source URLs, old comments | Leave as written |

Identify the installed **generation** from its version, provenance and source.
Never infer it from a prefix, namespace or display label: legacy OSM 0.1.x already
used `osm-*`, `OSM.md`, `OSM_FORMAT` and `OSM:BEGIN`, current AIOS uses other
names, and the new OSM reuses `osm-*`. A renamed label is not a migrated package,
and a legacy OSM block is not the new identity or something to delete.

## Record the baseline

Keep this per host, account and harness in the existing
[adoption record](adoption.md), privately:

- the installed generation, version, source revision or manifest, and namespace
  and invocation names;
- the manual and scheduled standing calls that invoke it, such as recurring
  prompts, automations and skill chains;
- the context home and its IDs, source keys, user-authored rules and the AI
  Operating Model link. Hosts can differ: one harness may route to a file home
  while another routes to Notion. Preserve each one; do not silently replace it;
- the permissions and connectors it relies on;
- the current, scoped recovery route that restores today's working state.

An unknown entry stays a named gap. A consumer you cannot reach, such as a project
outside this host's access, stays a required row marked unknown, not "not
applicable".

## Gates before cutover

All of these must hold for the host in question:

1. **The exact candidate** from the package's owner: an immutable source revision,
   package and manifest identity, a compatibility map from old to new identifiers,
   the supported native install, upgrade and recovery route for this harness, and
   the owner's qualification proof (clean install, upgrade keeping the existing
   home, mixed installations, fresh-session discovery and invocation).
2. Owner authority for this host, account and scope.
3. An agreed idle checkpoint for the affected work, and its holder.
4. A consistent **current** recovery copy on the same host, made or refreshed at
   that checkpoint and verified immediately before any effect (step 5 below), with
   the recorded immutable baseline identity and its supported native recovery
   route. A copy taken earlier does not satisfy this gate by itself.

A missing gate is a blocked field naming its holder. Do not invent install
commands, URLs or controls to fill it.

## Cut over one host

1. Inventory and classify, as above.
2. If useful, privately take a preliminary copy of the program, registration and
   context-instruction files in scope, with their full modes. It is only
   preliminary: affected work may still change those files, so it does not
   satisfy the recovery gate.
3. Select the verified candidate and the compatibility route for this host's
   generation.
4. Reach the idle checkpoint with the affected work's holders. Quiesce only the
   affected work; healthy independent work continues, and unrelated running work
   is not ended to rename it.
5. **At that checkpoint, before any native effect,** establish the current
   recovery copy:
   - Confirm every relevant holder is accounted for and the scoped sources stay
     quiet.
   - Make or refresh the copy on the same host, with full modes. Check that the
     source is stable before the copy and after it, and that the copy matches the
     current files: the same file set, bytes, sizes and full modes, and internal
     links where they matter. A preliminary copy counts only after this fresh
     comparison. If anything changed, refresh and reconcile it, keeping existing
     recovery material.
   - Keep the recorded immutable baseline identity bound to its supported native
     recovery route, and preserve the current home, IDs, user rules and
     permissions. Do not copy authentication or profile roots.
   - Stop before applying on an unknown holder, a failed consistency check, new
     editing or an uncertain effect. Use no manual cache, mode or grant edits and
     no custom fence.
6. Apply only through the harness's supported native help, plugin or upgrade
   controls that the candidate names. When the new identity is a new selector,
   as `osm` is for `aios`, this installs it; it is not an in-place update of the
   old one. Record the old source's exact ref and scope first.
7. Verify that the installed payload matches the candidate's manifest, the native
   registration shows the new identity, and unrelated configuration is unchanged.
8. Before acceptance, disable the old active source through the candidate's
   qualified native control, so no session sees two effective sources. Where the
   candidate documents a version-checked control for exactly that one
   registration, use only that control; never edit configuration wholesale or by
   hand. If no supported disable exists, use only the candidate's supported
   removal and recovery route at the idle checkpoint.
9. In a fresh target session, verify discovery, display, invocation and one real
   use that reaches the same AI Operating Model, home and IDs. Check that the
   standing calls resolve.
10. Only after that acceptance, and once no session or profile depends on it,
    retire the disabled old registration through supported controls, leaving one
    active family.

Record one outcome per host: **changed and verified**, **already current**,
**blocked** (with the dependency and holder), **unavailable** (not migrated), or
**mixed, stopped**. Stop on an ambiguous generation, an unsupported native step, a
failed check or an uncertain effect. After a partial effect, reconcile the actual
state before any retry or rollback. Never replay blindly, edit caches by hand or
change file modes to force a result.

## Roll back

Bind rollback to both the baseline's recorded immutable source or package
identity and the harness's supported native selector or route for exactly that
identity. A reused selector alone can resolve to something else. Keep the current
private state: context, homes, IDs and user rules. If an effect was partial or
uncertain, stop and reconcile the actual state before any rollback or retry. If
fresh-session acceptance fails, disable the new source and re-enable the old one,
or reinstall the exact old source through its native route; never delete or change
data homes or authentication. Then verify in a fresh session that the old calls
work again. Rolling back deletes no
context and no legacy blocks, and uses no invented command, cache edit, mode
change or grant.

Agentic Systems #93 stays open until each applicable host and consumer has its own
recorded outcome.
