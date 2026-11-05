# Factory definition and source ownership

Revision: 0.1.33 · Updated: 2026-11-05

The [Notion YAML code block](https://gustavanderson.notion.site/4056d2e17f56811b96fec7b970741916) is Factory Lab's only editable declaration. [factory.yaml](../factory.yaml) is a version-marked export: one small description of its purpose, context, roles, selected methods, review
settings, automation and routine ideas and evaluation proposals. An adopting project chooses its own declaration and context home. A repository is optional for non-software work.

## Declaration, configuration and evidence

AgentOps reads the declaration and resolves its linked methods. It does not start
a Factory service. Listing a role does not launch an agent; listing a recipe does
not schedule it. `status: candidate` and the unqualified recipe status are deliberate.
Current owner instructions, project rules and holds retain their authority.

The fields are our small project convention, inspired by Warp, not an Agent Skills
standard or a compatible Warp configuration. Native tools enforce only their
actually configured controls. CI, access permissions and selected runtimes can
enforce parts of the method after setup; prose and YAML do not apply those controls.
Future mapping to a native consumer requires its own accepted work and live proof.
No parser, reconciler, workflow engine or synchronization service is added here.

`context` identifies the entry, library and native records. `agents` names the
lead and optional bounded setup/evaluation roles; `work_modules` selects domain
methods without requiring a separate agent for every skill. `policy` selects
review settings and references the AgentOps skill's `references/policy.md` in its
native Files folder. Limits must be made concrete for an actual run. `evaluation`
lists proposals separately from qualified benchmarks. `operations` links to ideas and records
open and selected Lab choices; it is not an observed inventory of enabled native automations.
`qualification` routes to evidence, which must describe the actual installation.

## One editable original

| Artifact | Owning source in this recipe |
| --- | --- |
| This project's declared composition and source routes | The Notion YAML code block; `factory.yaml` is a labelled export |
| Shared architecture, authored skills and common policies | [Public Notion guide and Factory Skills](https://gustavanderson.notion.site/Factory-a-practical-guide-4046d2e17f568159a603de2dd6b91c2a) |
| Code, tests, CI/CD, applied native configuration, technical tasks and PR evidence | Their native repository/tool/tracker |
| Detailed history, logs and usage | The native agent tools |
| Credentials and private installation facts | Native secret stores and existing private project records |

Notion owns and explains the declaration. AgentOps reads it there, or uses an explicitly selected reviewed export at its recorded version. A requested composition or shared skill/policy change ends in its owning Notion source. Produce a versioned Git export only for a reviewed release, reproducible experiment or migration. Exports record the canonical code block's UTF-8 SHA-256 (LF, trailing newline) and the canonical code block's last-edited timestamp as well as the declaration version. Preserve that source/version and content snapshot; do not silently refresh it mid-run. No agent maintains parallel originals or automatic two-way synchronization.
Notion is replaceable; Databricks remains a parked enterprise recipe, not a dependency.

The existing Git skill bundles remain the released reference for their own
versions. Notion's core authoring edition is labelled separately from those
released references. Before a source cutover, review and verify the full portable
export, required references and intended native loading. A saved page, native
skill designation or valid YAML is not installation/discovery proof. Benchmarks
must fix the declaration and skill revisions as well as task/environment inputs.

## Portable skill exports

The shared core is authored in the public Factory Skills library. The `0.1.23`
distribution introduced exports of `factory-foundation`, `factory-agent-ops`, `factory-entry`
and `factory-evaluate`, with their complete supporting resources. Foundation's
references retain the accepted host, recovery, owner-entry and optional method
migration work from #85, #92 and #94. Updating this source does not install it in
an existing project.

Software and defence skill files keep their reviewed source versions; their
Notion entries identify them as released references. The `adlc/` directory is a
retained distribution path, not a requirement that the shared evaluator or every
Factory project is software work. Native loading and one real Lab task remain
separate acceptance work.

For 0.1.26, the native Skills API snapshot supplies AgentOps/Foundation and all
their supporting files. The portable export normalizes native frontmatter,
Notion-only preambles, line breaks and inline-code markup, restoring portable relative reference links; supporting files retain
exact source bytes. Existing software/defence versions remain unchanged. The PR
records the selected native snapshot and file hashes separately from installation proof.

A maintainer changes an owning Notion source and explicitly exports the selected
revision and resources. Review and record the actual readback, then freeze the
portable candidate for checks and release. Do not infer that merely fetching a
page exercised Notion's Skills API or installed its directory in a harness.

## Documentation reconciliation and propagation

[`docs/sources.json`](sources.json) records each public artifact's owner, label and stable Key: the
Notion page that is the original, or the Git path that is the original or a deliberate export.
`scripts/reconcile.py` runs in CI on every pull request and main merge. It reports a visible
NO-OP, CHANGES, ATTENTION or CONFLICT result in the job summary and as an artifact. A Git edit
of a Notion-owned export without a new canonical binding (skill metadata, or the declaration's
recorded hash), an edited released reference, a removed artifact still marked active, an
unowned path or a private path is reported; a conflict fails the check. With a frozen canonical
snapshot (`scripts/notion_snapshot.py`, read-only), it also compares each export with its
original. It normalizes Notion's rendering and compares supporting files byte for byte. A newer
original stays "export pending"; Git never overwrites it.

`scripts/publish.py` writes only Git-owned projections to one dedicated public status table:
the release label (released edition or main working revision), the Lab workspace declaration
and each skill's distribution state. It never writes a Notion-owned original. One run at a
time marks propagation pending, upserts rows by Key and content hash, and reads an uncertain
write back before one same-identity retry. It then reads the affected set back, plus anonymous
access, before marking it complete; a failure stays visible. The publishing workflow stays
inactive until a dedicated connection, limited to that public table, is provisioned. Main
working revisions are never relabelled as releases: a release is the tag that matches
`VERSION`. These checks verify sources and their propagation, not installation or adoption.

## Inspiration and credit

The architecture is substantially inspired by Zach Lloyd and Warp's
[The Factory Stack](https://www.warp.dev/blog/the-factory-stack) and
[Warp Factories examples](https://github.com/warpdotdev/warp-factory-examples),
including the principle of versioned factory definitions. Their product uses
its own native configuration tree and runtime. This is an independent adaptation
to a portable method across domains and native tools, with no compatibility or
affiliation claim. Arc' It AI branding retains its [separate terms](../assets/branding/README.md).
