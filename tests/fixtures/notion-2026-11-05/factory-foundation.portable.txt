---
name: factory-foundation
description: Prepare or assess a factory's agent environment, project foundation and operating conditions for the intended work, across software, BI, defence and research.
license: MIT
metadata:
  version: "0.1.31"
  updated: "2026-10-30"
---

# Factory Foundation

Use for requested setup, adoption, migration or readiness assessment. Assessment is read-only. Preserve the project's purpose, existing tools, instructions, artifacts and useful work. Setup does not admit new product work.

Identify the owner, intended outcome, project records, execution environment, operator entry and delivery destination. Recover facts from the actual sources before asking the owner to repeat them. Use the existing project/adoption record; do not create a second tracker. Resolve the assigned Factory declaration from its owning context source. In our Notion recipe, the YAML code block is the original; a selected `factory.yaml` export records a particular version. Read its declared composition and source routes. It records intended choices; verify applied native configuration separately and preserve existing authority and holds.

## Foundation scopes

**Agent environment:** selected client/host, native agent tools and models, assigned skills, identities/connections, effective permissions, native history, startup and recovery. T3 Code is a reference workspace, not a required Factory server. Another native tool is suitable only after its needed loading, execution and access behavior is checked.

**Project foundation:** authoritative context, goal and mandate, selected domain methods, native artifacts, meaningful acceptance checks and applicable standards. Software may use a repository; BI may use models and workspaces; research may use documents and datasets. Keep their native sources.

**Operations & maintenance:** the work/test/delivery/operating environments the task needs, observable failures, updater ownership, maintenance windows, recovery and relevant ongoing care. The agent host and the delivered product may run on different systems. A prototype does not require every production control.

These areas are preparation scopes, not three compulsory machines or access levels. Prepare only the capabilities the intended work requires. Reuse unchanged proof; recheck the affected capability after a relevant version, account, permission, configuration or dependency change.

## Adopt or update an existing project

Use [the adoption guidance](references/adoption.md#update-an-existing-project) when an existing project should align with a selected reviewed Factory revision. Compare installed methods and local adaptations before changing files; preserve product work, context and current authority. A project visible in a workspace is not necessarily an adopted installation.

## Establish context and skills

Resolve each artifact's original source. In the selected Notion recipe, shared method, policies and authored skills can live in Notion; project-native artifacts and technical work records remain in their native systems. Notion is replaceable. Until an explicit cutover, an existing source retains its authority for its version.

Before a project has its own Factory, the owner's Planning Agent can ask Foundation to prepare it. Select or create that project's context home, reuse its existing sources, and prepare only the declaration, skills and access the intended work needs. Its product goals, architecture and delivery belong there; the public Factory guide supplies reusable methods to select or link, not a document tree to clone. Hand the verified setup and remaining gaps to the project's AgentOps.

Keep project bootstrap instructions thin: common constraints, source routes and checks. Assign the role and selected skill explicitly; a role title or `AGENTS.md` does not load every skill or grant access. Preserve required references in the selected skill bundle. Identify source/version when materializing a worker's files or adopting a reviewed distribution. Do not invent a sync service or silently refresh installed skills.

## Prove the boundaries and operation

- Read the actual versions, selected provider/account, tools and effective native settings. A binary, connection, copied skill or available model name is not a working installation.
- Separate the human's personal access, the lead's bounded coordination access and the worker's assigned task access. Reviewers/evaluators are bounded workers, not administrators.
- For each source or project-service connection, agree its targets and operations, credential's OS account, storage and delivery, expiry, revocation route and responsible holder. Check actual allowed and refused access. For GitHub, use the scoped connection guidance in [references/github.md](references/github.md); a personal login or role name is not proof of the agreed boundary.
- Where an agent must use a credential without receiving its value, use a native credential broker outside its execution boundary. A secret store or redacted field does not establish this; readable mounts and environment variables deliver the value. Bind credentials to the selected project, environment and role through native controls, keep only references in context and declarations, and verify useful service access, an out-of-scope refusal, unreadable raw values, wrong-environment refusal and withdrawal of access, including cached credentials and global fallback.
- Selection of context is coordination; service permissions, OS/environment boundaries, mounts, network and tool controls enforce access. A worktree separates changes, not readable files or credentials.
- For the Notion recipe, give the lead a scoped connection to its selected project pages, with only the read, update and insert operations authorized for its work. The Lab's grant is Factory-only; personal Data & Context is excluded. Keep real service credentials outside the execution boundary through a native broker where required. Supply workers selected skill/context files, never the lead's connection. A same-environment process shares its brokered reach; a worker that must not have it needs a separate boundary. Read-only access cannot write progress; use the native task record or a scoped handoff until an authoring route is authorized. If an inherited connector exceeds the accepted task access, hold dependent worker execution until the exposure is removed, isolated or explicitly resolved by the owner; do not treat a role instruction as the repair.
- Check an allowed operation and one that should be refused in the actual worker/tool environment. Record success, approval request, permission denial and OS refusal distinctly. A document's claim is not proof of enforcement.
- Confirm actual project checks and relevant failure paths. Distinguish source inspection, a rehearsal, installed behavior and the delivered outcome. Domain checks must assess the original criteria. If no suitable domain module exists, agree task-specific checks and disclose the gap; do not imply that a BI or research module is already shipped.
- Agree update ownership for a shared host; this remains an owner choice. Until it is set, route update decisions to the owner. An idle maintenance window has no active or unknown writers on the affected host. Reconcile them before changing versions, stopping services or rebooting. Keep a recoverable starting state, verify affected operation afterwards and preserve private native history.
- Qualify the recovery behavior required by the intended unattended work on disposable tasks. Unqualified restart or update behavior holds actions that depend on it; other explicitly authorized work may continue only where interruption is harmless and the recovery limitation is disclosed. Updates, approval prompts, machine login and encrypted-disk unlock may need different recovery routes. Native scheduling is optional and needs an authorized, tested configuration.
- Keep credentials in native secret stores and sensitive host/account details in private installation records. A private record of a permission does not apply it or enforce its expiry.

Preserve explicit admission/delivery delegation and stop conditions. A new grant must identify the needed operation, target, authorizer and removal condition. The lead role alone grants no administration or delivery authority.

## Hand over a readiness result

For each required capability, record its scope, owning source, disposition and retained evidence:

- **Verified:** an actual check/readback or applicable dated proof supports the claim.
- **Required gap:** unchecked, inaccessible, conflicting or failed prerequisites remain visible, with the next action and responsible holder.
- **Conditional / not needed:** explain why the intended work does not depend on it.

A required gap holds dependent work, not unrelated authorized work. A recorded gap is not readiness. Hand the result to AgentOps, which maintains project choices within its mandate and routes concrete setup repairs back to Foundation. The work module verifies each changed deliverable and updates affected context.

For an optional owner-side entry, use `factory-entry` and the selected native installation route in [references/setup.md](references/setup.md). For a personal method package changing identity, consult [references/method-migration.md](references/method-migration.md); Factory depends on no such package.

For software/T3-specific preparation, consult only the relevant bundled reference: [references/adoption.md](references/adoption.md), [context.md](references/context.md), [engineering.md](references/engineering.md), [ci-delivery.md](references/ci-delivery.md), [github.md](references/github.md), [setup.md](references/setup.md) or [workspace.md](references/workspace.md). These imported references retain their observed versions/dates; old worked examples are not current installation proof. Qualify them against the chosen tools before applying them.

Factory Foundation installs no Factory daemon and grants no authority beyond the request.
