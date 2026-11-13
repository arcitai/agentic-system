# Contributing

Revision: 0.2.0 · Updated: 2026-11-13

Start with a concrete problem, the applicable project goal and observable proof.
Use an issue or accepted brief; research may end with a decision rather than code.
Preserve the small method-only scope in [VISION.md](VISION.md).

Resolve [source ownership](docs/system-definition.md) before editing. Shared methods are authored in Notion; a reviewed distribution uses portable bundles in `foundation/`, `entry/`, `evaluation/` or `defence/`. Existing Git bundles remain authoritative for their released versions. The Notion core edition and its complete supporting resources are exported deliberately for this distribution. Do not maintain two editable originals. A release must retain the exact source/version and required resources; it must not silently export a newer source or require live Notion access to function.
Supporting references belong inside the skill directory so staging keeps them
usable. The root documentation is for maintainers/operators and is not a hidden
runtime dependency. Preserve the existing MIT attribution.

## Versions and a small documentation surface

`VERSION` identifies the package release. Each skill uses the standard optional
`metadata.version` and `metadata.updated` string fields. Other maintained Markdown
starts with `Revision: X.Y.Z · Updated: YYYY-MM-DD`. The revision is the package
version in which that file was last edited, not a separate release stream. Advance
it and the edit date when changing that file; unchanged files keep their revision.
Update a skill's metadata when its bundled references or scripts change too.
Git and the reviewed PR hold the change history; do not add a per-file changelog.
Templates under `.github` are exempt from the visible revision line so their
metadata does not leak into issues or PRs.

These dates describe source edits, not testing or installation. Keep each observed
version/date next to its claim, including failures and pending checks. A release
must not refresh historical observations merely by changing document headers.
Foundation establishes this convention, the selected work module updates affected sources and review
checks them, and the project agent resolves concrete drift within its mandate.

README routes to the public architecture/context entry; setup remains the installation/maintenance path. The chosen context home owns the declared composition; our recipe uses one YAML code block in Notion. `system.yaml` is only a version-marked export and links to shared methods rather than duplicating their full policy. Edit the original, then make a deliberate reviewed export; do not maintain an agent that synchronizes two editable copies. It is not consumed by an Agentic System runtime; the working project agent interprets it. Keep
conditional detail inside the affected skill and keep current qualification here.
Historical research, migration inventories and old rehearsals remain available
in reviewed releases and PRs instead of becoming permanent onboarding steps.
Adopting applications retain their own documentation/versioning conventions.

The layout follows the [Agent Skills specification](https://agentskills.io/specification):
small discovery metadata, focused instructions and references loaded only when
needed. MIT permits reuse of Agentic System's method, code and documentation; the
[branding exception](assets/branding/README.md) still applies. A license grants
no system or account access.

## Verification and delivery

Before a PR:

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests
```

Exercise changed staging behavior on disposable destinations. For substantive
instruction changes, rehearse a realistic task in a separate context and retain
sanitized inputs, outcome and limitations. Include failures and fixes. Checks
must demonstrate decisions or artifact behavior rather than count wording.

Separate review assesses the accepted scope and actual candidate. A human may
delegate delivery under project rules; neither a skill nor a green workflow grants
it. New commits require refreshed affected evidence. GitHub protection may require
a separate GitHub reviewer identity; a second model on the author's account does
not satisfy that rule.

Release reviewed commits with a Git tag matching `VERSION` and a GitHub release.
Consumers can clone that tag or download the source archive. There is no npm
package or daemon to publish. Verify the tag, checks and release contents after
publication. Describe native setup and qualification limits in release notes.
For recovery, select the previous reviewed release and diff staged skills against
the installed copy; preserve local adaptations and private native state.

Retain the human author and genuine coauthors in the final commit, including
squash merges. Use each contributing harness's native attribution; Codex uses
`Co-authored-by: Codex <noreply@openai.com>`, while Claude uses its native selected
model attribution. A reviewer is described in the PR's checks, not automatically
made a coauthor. Coauthorship changes credit, not GitHub authentication or access;
the contributor graph also depends on GitHub's email and branch rules.
