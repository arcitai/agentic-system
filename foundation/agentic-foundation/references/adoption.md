# Adoption record

Revision: 0.1.29 · Updated: 2026-10-30

Foundation identifies the appropriate existing project/adoption record and
establishes the relevant choices. AgentOps maintains them and scoped exceptions
for its current project within the owner's mandate. Extend that record;
do not create a separate register or require the whole inventory for every project.
Record choices that need to survive the task, affect later work or need removal,
not every transient task choice. Unknown is a visible gap, not a made-up default.

Name the record's actual maintainer: a person/operator or concrete authorized role,
the portion and location each may maintain, and the access limit. If the project's
lead cannot read or update the private record through its effective boundary,
record that limitation and the supported handoff, such as sanitized changes passed
to the operator who holds access. Do not claim independent lead upkeep, copy private
details into a second register or broaden access to close the gap.

Keep shared method and policy in their chosen authoring home; our Lab uses Notion. Project-native configuration and technical records remain in their own tools. Keep host
identities, private paths, account references and sensitive evidence in the existing
private installation record; share only sanitized summaries. Credentials belong
only in actual secret stores. Executable native configuration is the source of
truth for applied state: link to its owning source/control instead of copying
values uncritically. An observation may quote a safe value with its source and date.

## Update an existing project

Use this route for an existing repository or other project adopting a newer
reviewed Agentic Systems revision. The setup request changes the method within its scope;
it does not admit new product work or migrate every project on the host.

1. Identify the current lead, actual workspace, source/context routes, installed
   skill versions, local adaptations and existing holds. Read the project's own
   instructions, checks and delivery rules. Keep the existing adoption record.
2. Select an immutable reviewed distribution or a specific context-home revision,
   including the full required references. Compare old source, local changes and
   the candidate. Preserve useful adaptations; resolve conflicts rather than
   replacing the project with Agentic Systems Lab's settings.
3. Update only the affected skills, thin bootstrap routes and documentation in
   their owning sources. Preserve product files, work in progress, personal
   context, native history and credentials. Broader connector, host or access
   changes keep their own authority and recovery requirements.
4. Use the chosen tool's supported loading/adoption route. Verify the actual
   installed bytes, fresh-session discovery or explicit loading, and a bounded
   task with its relevant checks and independent review. If live adoption is
   outside this task, report the source as prepared and leave those checks open.
5. Record the selected revision, retained adaptations, demonstrated result and
   remaining gaps. Keep the prior working revision and supported recovery route.
   Recheck affected capabilities; do not repeat unrelated host qualification.

A repository's `AGENTS.md` can point to the selected methods and shared rules;
it does not need to copy them all. A declaration belongs in the project's chosen
context home. Notion is our reference, not a dependency for using a released bundle.
For an optional method package changing identity, use [method migration](method-migration.md).

### Notion skill directories

In our Notion recipe, the lead's existing scoped connection reads a skill's whole
directory with `GET /v1/ai/skills/{id}`: a `version_id` and a temporary signed
archive containing `SKILL.md` and its **Files**. `POST /v1/ai/skills/{id}/upload`
writes a gzipped tar with `SKILL.md` `name`/`description` frontmatter and replaces
the page's title, Description, content and Files. Before uploading, back up the
complete current directory and compare its `version_id` immediately beforehand; the
API has no precondition field. After an uncertain result, reconcile the same object
before any retry. Read back the new `version_id` and the exact supporting-file bytes.
Notion renders the native `SKILL.md`: check semantic correspondence with the portable
file, not byte identity. `version_id` is not the package version; update the page's
Version, Source and Status explicitly. Ordinary page-property REST does not expose
Files. Workers do not receive this connection. See the
[Skills API](https://developers.notion.com/reference/agent-skills/get-skill-directory)
(Notion-Version 2026-03-11).

## Persistent choices and exceptions

Use short prose or a small table with only meaningful fields:

| Distinction | Useful content |
| --- | --- |
| Scope | Affected project, environment and role; requested scope versus actual account, provider, global, project, chat or task scope |
| Intent | Requested or approved value/capability, source, owner, authority and reason; the default displaced by a scoped exception |
| Application | Owning native configuration/control, actual applied scope and application date, or unapplied/uncertain status |
| Verification | Dated effective-state readback and relevant operation/outcome, with version and evidence; keep unverified claims visible |
| Upkeep | Relevant review trigger, expiry/removal condition, responsible owner and rollback/recovery route; verified removal when due |

Requested intent, approved intent, applied settings and observed behavior are
different states. A provider-wide setting or grant is not project isolation. If
the native control cannot isolate the requested project, record that limitation
and resolve an authorized supported boundary before applying; do not silently
propagate the choice to other projects. The record grants no authority, enforces
no access and applies no configuration. Agentic Systems Markdown does not apply itself.

For an authorized persistent change:

1. Read effective native state and its source, including overrides; assess the
   real scope and affected projects before changing it.
2. Reuse existing authority and its conditions. Resolve only missing authority or
   material new scope/risk under the two decision points; retain the prior state
   and a relevant recovery route.
3. Apply through supported native controls and verify meaningful readback at the
   affected scope, plus the operation or boundary the claim relies on. A failed
   or uncertain apply remains unverified; reconcile actual state before retrying.
4. Update the existing record without secrets, preserving intent versus applied
   scope and observed proof. For a temporary grant or override, use native expiry
   where supported or assign its actual removal; verify revocation/removal when
   due and record the result. Prose expiry does not enforce itself.

Reconcile affected entries on relevant setup, configuration or provider upgrades,
incidents and task needs. Preserve unchanged evidence at its observed date; no
watcher or expensive full scan is required on each run.

The reviewable intent and reproducibility principle is informed by Warp's
[versioned definitions](https://docs.warp.dev/factories/factory-as-code/) and
[agent configuration](https://docs.warp.dev/factories/factory-agents/), read
2026-10-10. Agentic Systems retains its existing records and native controls, with no
imported schema or runtime.

## Relevant installation context

Reuse the following existing choice families only where they matter:

- Project, owner, approved vision, canonical instructions and actual repo/branch.
- Routes to relevant architecture, checks, dependency/configuration sources and
  operational guidance. Preserve the project's existing names and records.
- Execution host and OS identity, client route, service owner, native versions,
  provider profiles and billing/usage source: the provider account and history it
  covers, the native Usage view and filters used, known coverage gaps, and who reads it.
- Effective account/context boundary: account and organization, configuration home
  and launch overrides, loaded instruction/skill/plugin sources, worker-visible
  tools including account imports, scoped corrections and personal-client
  preservation or gaps. Keep configuration, CLI and actual-worker proof distinct;
  follow [the effective-account check](setup.md#verify-the-effective-account).
- Model profile: a small editable default per role or kind of work, such as lead
  research, implementation, independent review and small mechanical work, with
  any concrete exception and its reason. Use live native provider, model and option
  IDs/values. Mark each entry as owner-selected or proposed, and keep it separate
  from configured settings and observed child readback. Explicit owner choices
  prevail. Refresh it when models, requirements or retained outcomes change.
- Selected skills, Agentic Systems tag/revision, stage hashes, installed paths, preserved
  local changes and observed native discovery.
- The owner's own AI agent: which agent and harness hold `agentic-entry`, and its
  requested, installed, discovered and used states recorded separately. Also the
  current lead for each project it routes to, so a resumed caller can find the
  right recipient again.
- Ops thread identity, project/workspace binding, role/source paths, pin and
  auto-settle choice; explicit source loading distinguished from native discovery.
- Each client's saved service connection and Local environment choice; observed
  execution host, OS/account and workspace, distinguished from the client device.
- Selected update channels and native installer/updater ownership; checks versus
  automatic installs, idle/interruption rules, recovery and last observed result.
- Optional method packages the owner uses on each host, such as The Onlinesourdough
  Method (OSM): installed generation and version, invocation names, standing calls,
  context home and IDs, and the current recovery route, as in
  [migrating an optional method](method-migration.md).
- For a stronger worker boundary: the rootless-container or VM comparison, its
  evidence and the decision, as in the [setup guide](setup.md#1-choose-the-boundary).
- Host continuity, where chosen: the host coordinator's thread and mandate, and
  the projects whose leads it coordinates with. For each startup stage (disk
  unlock, headless service boot, network routes, desktop autostart after login,
  power policy), record its owner and last dated readback; see the
  [setup guide](setup.md#keep-the-host-ready-after-restart).
- If scheduled maintenance is selected, its agreed opportunity: its native scheduler and target,
  each component transaction and its owner, the last actual trigger and what it
  observed (no-op; deferred with reason, next action and holder; or the stages
  installed, restarted and continued that it reached), the authority it used, and
  the retired duplicate after a migration.
- Recovery: the private recovery copy's location, holder and scope, the last
  verified same-host restore, and the operator able to act while the service is down.
- AgentOps scope (Agentic Systems and the adopted repository) and the narrower ADLC task
  workspaces. Record each extra grant separately from that baseline: who or which
  role, target, environment, purpose, date, authorizer, expiry/removal condition
  and readback, without secrets; user-editable versus managed controls.
- Effective filesystem/network/tool boundaries, allowed data destinations,
  deployment credential requirements and private security reporting route.
- Work-status source and actual Project/field/label identifiers; priority and
  readiness policy; issue intake and trusted owner identity.
- Admission authority and delivery authority separately, including explicit
  delegation and conditions. State any pause/risk conditions that change them.
- Real checks, required GitHub rules, review context, release/deployment policy
  and recovery route.
- Application environments separately from the execution host: chosen platform,
  artifact/deploy route, data/migrations, allowed agent access, rollback and the
  last observed restore where recovery of state matters.
- External services/connectors and their dependent features: configuration owner,
  required access, actual operation checked and remaining gaps. Installed,
  authenticated, resource-accessible and usable are separate observations.
- Operational signals, their locations, access/redaction/retention, response owner
  and runbook. Retain the result of relevant health, alert and failure-path checks.

For each claimed capability retain the tested revision/version, action, outcome,
date and evidence. Relevant proof includes:

1. Correct native account, tools and skill discovery at the selected scope.
2. One real task through independent review and authorized delivery.
3. Permission refusal/unavailable provider is visible and does not become success.
4. Client disconnect and reconnect; then controlled interruption/restart with
   native state reconciled and no duplicate writer or replayed external action.
5. The actual phone/remote decision route if selected.
6. A representative isolation check for each trust boundary being claimed.
7. Readback of actual GitHub status/protections and delivered application behavior.
8. Where host continuity is claimed: boot, login, disconnect and reconnect, and one
   actual scheduled wake, each recorded separately. A wake alone is not reboot or
   recovery proof.

Keep source inspection, disposable rehearsals and live installation evidence
distinct. One successful run qualifies that path, not every model or future update.
Record the next required observation for each incomplete capability.
