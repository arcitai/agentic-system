# Definition and source ownership

Revision: 0.2.3 · Updated: 2026-11-25

The [Notion guide](https://www.notion.so/4046d2e17f568159a603de2dd6b91c2a)
owns current shared method authoring. A project chooses its own small definition
and context home. The optional Git-owned [project brief](../templates/project-brief.md)
helps put useful context in an existing project record. Its statements record
intent and authority; native systems enforce access and configuration.

## Current authoring and selected exports

On 25 November the live Notion catalog contains six Core methods (Foundation,
Brief, Council, Takeover, Full Stop and Output) and the optional Software method
New Feature. Their pages and Files own current instructions and version metadata.

This repository's 0.2 portable line retains Foundation 0.2.1, Entry 0.2.0 and
Evaluate 0.2.0 as earlier Notion exports, plus the Git-owned optional Defence
method. Those selected files and bindings are preserved; they are not a mirror
of the later six-method Core. Entry, Evaluate and the Defence snapshot are not
rows in the current seven-row live catalog.

[system.yaml](../system.yaml) retains the exact 13 November Lab 0.9 export and
its recorded canonical hash. On 25 November the public
[System definition](https://www.notion.so/4056d2e17f56811b96fec7b970741916)
page contains general project guidance and no Lab YAML block. This is an
observation of the current source, not a claim about when or why it changed.
The unavailable live block cannot be called IN-SYNC with the frozen export.
Keep the selected snapshot until a separate reviewed source/adoption decision
resolves its next export. This documentation release changes no Lab configuration.

## What the dated Lab declaration describes

`work` selects one continuous project agent and conditional help. `model` records
Lab's existing owner-selected model and reasoning setting. `methods` links to the
selected shared capabilities. `policy` routes to Foundation's portable rules and
records Lab's retained two-review default. That count is a project choice, not a
framework minimum. `workspace` states the selected client/channel and target
version; its `installed_state` routes to private native proof. `operations` and
`qualification` keep scheduling, maintenance ownership, evidence and holds visible.

These are a small project convention, inspired by Warp, not an Agent Skills
standard or a compatible Warp configuration. A listed method, recipe or model is
not installed by being named. Native tools enforce their configured controls.
Requested, approved, applied and observed settings remain separate facts.

## One original per artifact

| Artifact | Source and ownership |
| --- | --- |
| Current general method and six-method Core | The public Notion guide and Skills library |
| Selected 0.2 Notion skill exports | Their Notion originals at the recorded revisions; Git preserves the frozen exports |
| Lab 0.9 declaration | Its recorded 13 November Notion source and frozen Git export; the current guide has no matching live block |
| Optional project brief | `templates/project-brief.md` in this repository; Notion links to this original |
| Optional defence skill | Its Git directory; Notion holds a released reference |
| Code, tests, delivery and qualification records | Their native repository, tool or tracker |
| Diagram artwork for a reviewed edition | The versioned Paper document and its derived SVGs in `docs/diagrams`; Notion embeds their rendering |
| Detailed conversations, runs and usage | The native agent tools |
| Credentials and private installation facts | Native secret stores and private installation records |

A method, composition or policy edit ends in its owning source. A deliberate export
pins the selected edition for review, release, a reproducible experiment or migration;
never refresh a running task silently. Notion is replaceable and is not a runtime
dependency. An exported declaration records the canonical block's UTF-8 SHA-256
(LF, trailing newline), edit timestamp and definition version.

For this 0.2 portable line the groups are `foundation/`, `entry/`, `evaluation/` and
`defence/`. Entry is optional outside assistance; Foundation prepares and maintains
the garden; Evaluate compares alternatives when evidence can change a decision.
In this selected export line, the earlier internal AgentOps, Brief and software
stage packages are retired. Their stable manifest keys and dated evidence remain
as history. The same Brief page is active as 0.3.0 in the later Notion Core;
its retired 0.1.34 export entry does not describe that current authoring state.
Entry's status guidance and Foundation's continuity rules remain in the 0.2
exports. A project selects sufficient methods for its own work.

The [method history](https://www.notion.so/4176d2e17f56813b891fe3d3db612c52)
and the `v0.1.34` tag retain the earlier arrangement. Historical references inside
Foundation identify their observed versions; they are not current installation
proof or compulsory onboarding instructions.

## Deliberate export and reconciliation

[`docs/sources.json`](sources.json) identifies this distribution's artifacts by
stable Key, owner, label and native identity. Its existing export bindings and
retirement entries record the selected 0.2 line; it is not an exhaustive inventory
of the current 0.3 Notion catalog. Do not reuse retired keys for different artifacts.

- Notion-owned originals reach Git through a frozen read-only Skills API snapshot
  and `scripts/export.py`. The export restores portable frontmatter, headings and
  relative links, copies supporting bytes, and binds the revision and version.
  Unresolved links are reported rather than guessed. A changed original is export
  pending; Git never overwrites it.
- Git-owned released references reach the existing Notion page through
  `scripts/publish.py`: complete files and Version, Status and release-pinned Source.
- A pending editorial handoff stays visible until its actual canonical readback
  contains the intended change.
- Git-owned explanations, checks, diagram editions and technical records are
  published by this repository.

`reconcile.py` runs on pull requests and main pushes, reports NO-OP, CHANGES,
ATTENTION, CONFLICT, or UNVERIFIED when originals were not read, and fails on
conflicts. It catches unbound edits to exports, unversioned released-reference
changes, active missing artifacts, unowned/private paths and source-ownership
changes lacking a decision record. With a canonical snapshot it also checks the
declaration header and the actual body hash. IN-SYNC needs
canonical, bound and Git versions to agree, including instructions, link targets
and required resource bytes. A successful source check is not installation proof.

## Released-reference publication

Publication is serialized from main or the matching `v*` tag. The status
`agentic-system/docs-propagation` becomes pending before any write. Writes use the
existing page identity. An uncertain result is read back before one same-identity
retry. A newer Notion edition is not downgraded. A page outside Released reference
status is never overwritten without an explicit manifest cutover decision.

A retry proceeds only if readback confirms the state from before the write.
A concurrent edit or unreadable result stops the run. Files not represented in
the released Git source are preserved for an explicit decision, and an older
checkout cannot move an existing source pin backwards even at the same skill version.

After writes, read back every active released reference's files, body and
Version/Status/Source, retaining revision and file hashes. A change without its
matching release tag stays release pending. Anonymous readback must stay on the
page's host and contain its expected name, version and first instruction: a 200
login page or empty shell is insufficient. Missing public proof leaves a visible
pending checklist. Retired pages are not publication targets.

Publisher success covers only the released-reference pages. It does not read back
the entire public guide or the Skills catalogue and its filters. The publisher is
not operational until its bounded live qualification passes. The first bounded live
publish, a read-only rerun and browser readback of the coherent public set remain
separate qualification work under #122. The workflow remains inactive until its
dedicated connection is limited to the guide subtree, its environment is restricted
to main and `v*` tags with a required reviewer, and tag creation is restricted.
No broad personal token is added to CI. An ordinary source revision is not a
release, and a saved page, valid package or positive review is not native discovery
or use.

## Credit

Inspired by Warp's [Factory Stack](https://www.warp.dev/blog/the-factory-stack),
[Factory examples](https://github.com/warpdotdev/warp-factory-examples) and the
selected sources in the [Reference library](https://www.notion.so/4176d2e17f568129ab71cfa0b2aecbd8).
This independent framework makes no compatibility or affiliation claim.
Arc’ It AI branding retains its [separate terms](../assets/branding/README.md).
