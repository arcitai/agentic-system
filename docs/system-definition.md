# Definition and source ownership

Revision: 0.2.0 · Updated: 2026-11-14

The [Notion YAML block](https://www.notion.so/4056d2e17f56811b96fec7b970741916)
owns Lab's declared composition. [system.yaml](../system.yaml) is its version-marked
export. The project agent interprets it; it grants no access and applies no settings.
An adopting project chooses its own small definition and context home. A repository
is optional outside software work.

## What the declaration describes

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

| Artifact | Editable original |
| --- | --- |
| Lab's declared composition | The Notion YAML block; the Git file is an export |
| General method, three shared core skills and their references | The public Notion guide and Skills library |
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

For 0.2.0 the portable groups are `foundation/`, `entry/`, `evaluation/` and
`defence/`. Entry is optional outside assistance; Foundation prepares and maintains
the garden; Evaluate compares alternatives when evidence can change a decision.
The internal AgentOps role, Brief and software stage skills leave the active
distribution. Their stable manifest keys, Notion pages, supporting files, releases
and dated evidence remain as history. Responsibilities from Brief now live in
Entry's status guidance and Foundation's continuity rules. A software project
selects sufficient native, project or specialist methods for its own work.

The [method history](https://www.notion.so/4176d2e17f56813b891fe3d3db612c52)
and the `v0.1.34` tag retain the earlier arrangement. Historical references inside
Foundation identify their observed versions; they are not current installation
proof or compulsory onboarding instructions.

## Deliberate export and reconciliation

[`docs/sources.json`](sources.json) identifies each artifact by stable Key, owner,
label and native identity. Do not reuse retired keys for different artifacts.

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
changes, active missing artifacts, unowned/private paths, invalid declaration
headers and source-ownership changes lacking a decision record. IN-SYNC needs
canonical, bound and Git versions to agree, including instructions, link targets
and required resource bytes. A successful source check is not installation proof.

## Released-reference publication

Publication is serialized from main or the matching `v*` tag. The status
`agentic system/docs-propagation` becomes pending before any write. Writes use the
existing page identity. An uncertain result is read back before one same-identity
retry. A newer Notion edition is not downgraded. A page outside Released reference
status is never overwritten without an explicit manifest cutover decision.

After writes, read back every active released reference's files, body and
Version/Status/Source, retaining revision and file hashes. A change without its
matching release tag stays release pending. Anonymous readback must stay on the
page's host and contain its expected name, version and first instruction: a 200
login page or empty shell is insufficient. Missing public proof leaves a visible
pending checklist. Retired pages are not publication targets.

Publisher success covers these active released-reference pages, not the entire
public guide or the Skills catalogue and its filters. The first bounded live
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
