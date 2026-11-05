![Factory — a method assembled from native tools](assets/branding/factory-banner.png)

# Factory

Revision: 0.1.33 · Updated: 2026-11-05

A portable method for using AI agents across software, BI, defence and research.
Start small, use existing tools, and add complexity when a real task needs it.

**[Read the practical guide and architecture](https://gustavanderson.notion.site/Factory-a-practical-guide-4046d2e17f568159a603de2dd6b91c2a)** — the public Notion home explains the method, diagrams, skills and current open choices.

Factory supplies methods and portable Agent Skills. Your chosen agent tools run
the work; their native configuration and service permissions enforce access.
T3 Code is our reference workspace. Codex, Claude Code or another capable native
setup can also be used after checking the capabilities the task needs. Choose
your own context home, tracker, source hosting and infrastructure.

## How it fits together

| Responsibility | Purpose |
| --- | --- |
| [Foundation](foundation/factory-foundation/SKILL.md) | Prepare the agent environment, project foundation, and operations and maintenance needed for the work |
| [AgentOps](agent-ops/factory-agent-ops/SKILL.md) | Lead one project: investigate, assign bounded work, coordinate review and deliver within the owner's mandate |
| Work modules | Supply domain methods and checks: [software](adlc/README.md), [scoped defence](adlc/factory-security/SKILL.md), and future dedicated BI and research methods |
| [Evaluation](adlc/factory-evaluate/SKILL.md) | Compare outcomes, defects, cost, time and human effort before recommending a change |

Independent review checks the actual result against the original requirements.
By default, use two fresh reviewers: one for objective/domain evidence, one for
qualitative intent, usefulness and experience. Delivery waits until both reviewers’ blocking concerns are resolved.
Projects and tasks can override roles, numbers and models within their mandate
and stronger requirements. Model judgments do not replace meaningful domain checks.

An optional [Factory entry skill](agent-ops/factory-entry/SKILL.md) helps your own
Planning Agent route requests to existing project leads. Each project keeps its
own AgentOps; Factory Lab develops this method rather than managing every project.

## Start with a new or existing project

1. Your Planning Agent can ask Foundation to prepare a new or existing project.
   Select the project's own context home and reuse its sources,
   useful conventions and existing checks; prepare only missing capabilities.
   Link the shared method rather than copying the public guide into every project.
   Follow [setup](foundation/factory-foundation/references/setup.md) for the
   selected native tools.
2. Select the declaration and skills, with their revisions. Our Lab's
   [YAML original lives in Notion](https://gustavanderson.notion.site/4056d2e17f56811b96fec7b970741916);
   [factory.yaml](factory.yaml) is a versioned export. AgentOps reads the
   declaration; it does not apply settings or grant access.
3. Give the project's AgentOps one bounded task. Check the result, get independent
   review, and deliver under the agreed authority.

**Already using Factory?** Use the same Foundation skill and its
[existing-project adoption guidance](foundation/factory-foundation/references/adoption.md#update-an-existing-project).
Compare the selected reviewed revision with local adaptations, update affected
routes and complete bundles, and prove discovery and use. A project shown in T3
has not automatically adopted the latest method. No extra migration agent or
synchronization service is needed.

## Context and distributions

Notion is our replaceable authoring home for shared methods, policies and skills.
The [Factory Skills library](https://gustavanderson.notion.site/5e1552911ffc42b8a999609cc6847a00)
contains their instructions and supporting files. Databricks remains a future
enterprise option. Project code, data, applied configuration, technical tasks and
results stay in their existing native sources. Keep one editable original.

A secret store protects stored values. When an agent must use a credential
without receiving its value, a native credential broker outside the execution
boundary can authenticate its service calls. Native controls and upstream service
grants still enforce what the agent can access. For details, see the public
[Context & access](https://gustavanderson.notion.site/Context-access-4056d2e17f5681e29517ecc664a137ed)
guide.

This repository contains reviewed portable distributions, bounded staging/check
helpers, and Factory Lab's technical work. Required references travel with each
skill. Use a reviewed release without live Notion access, or read the selected
Notion original and identify its revision. Changes go to their owning original
before a deliberate export; no process maintains two editable copies.
See [source ownership](docs/factory-definition.md) and [contributing](CONTRIBUTING.md).

## Where we are going

| Step | Status and next work |
| --- | --- |
| Method and distribution | The #98 transition is complete. Shared methods are authored in Notion and exported deliberately. Two independent reviewers are the default. Revision 0.1.29 corrects current Lab facts and adds Foundation's Notion Skills API recipe for reading and updating whole skill directories, without changing method rules. Revision 0.1.30 records the Lab-only issue-intake selection (declaration 0.5), also without changing method rules; [#80](https://github.com/arcitai/factory/issues/80) retains live account and connector acceptance. Main working revision 0.1.33 (unreleased) adds a per-artifact [source manifest](docs/sources.json), a visible documentation reconciliation in CI and a prepared, inactive public-status publisher ([#122](https://github.com/arcitai/factory/issues/122)); see [source ownership](docs/factory-definition.md#documentation-reconciliation-and-propagation). |
| Factory Lab | **Current (3 November 2026):** Lab Ops runs official T3 Stable 0.1.6 with the same Mac GUI app and pinned lead ([#34](https://github.com/arcitai/factory/issues/34#issuecomment-6613129194)). A scoped fresh-VM GUI restore from a retained archive worked: native readback matched the history, and the GUI showed a completed, a failed and the cancelled thread (labelled "Done") ([#32](https://github.com/arcitai/factory/issues/32#issuecomment-6604340468)). At manual scope, the existing unit stop returned 125 (not clean); a guest-first stop under a temporary no-restart setting returned 130 (clean). The 2 GiB worker default is evidenced only for one probe and one restarted reviewer; six workers are not qualified. Open: boot/login, unattended updates, permanent maintenance. No retirement; #114 held; general intake disabled; Incident A's lost histories stay recorded. Details: [qualification](docs/qualification.md). **Earlier dated history:** from the 29 October maintenance the server ran official T3 Stable 0.1.5. The three older Nightly 3796 baseline environments were retired on 30 October (stopped, disks and histories retained) and are no longer fallbacks. A same-host userdata restore on 29 October returned the same pinned lead and history. Earlier that day, the native controller cold-provisioned a digest-pinned image, and worker test data persisted through a parent SIGKILL. In R7, the lead created three fresh Stable 0.1.5 workers; after repair, two independent reviews accepted, the writer resumed useful model work in the same thread after restart and verified history archives preceded cleanup ([#32](https://github.com/arcitai/factory/issues/32)). On 29–30 October a whole-service stop was not clean (exit 125) and an idle guest TERM (exit 130) returned automatically once; that was before the 3 November measurements above. |
| Improvement | **Current (3 November 2026):** after the Lab Ops cutover (see the Factory Lab row's current summary), the same pinned lead completed useful native runs, and the checker failure on an ignored private task note was isolated as [#119](https://github.com/arcitai/factory/issues/119). One bounded native change cycle (Sonnet 5.5 High implemented; two fresh Opus 5.5 High / Fast off reviews each accepted) produced merged [PR #120](https://github.com/arcitai/factory/pull/120). One cycle makes no claim of universal correctness, cost savings or autonomy, and general intake stays disabled. The model choices are the owner's, recorded in declaration 0.7; Notion stays canonical and [factory.yaml](factory.yaml) is its labelled export. Counts and limits: [qualification](docs/qualification.md). **Earlier dated history:** On 30 October, rc1 completed useful model, review and delivery work from the restored Stable Ops in native Auto, with fresh Stable workers ([#32](https://github.com/arcitai/factory/issues/32#issuecomment-6512720017)). Later that day, a native schedule dispatched one queued message that started a finite lead queue, and an operator canary read and wrote skill directories through the Notion Skills API ([qualification](docs/qualification.md)). The Lab then selected one native issue-intake routine (declaration 0.5): a T3 schedule bound to the pinned lead every 180 minutes, whose reviewed mandate admits at most two new issue outcomes per window under the existing review and budget rules; its first dispatch was observed at 11:34 UTC on 30 October 2026. Open then: clean stop, boot/login, maintenance and updates, and GUI/new-VM archive restore (see the Factory Lab row's current summary for what 3 November changed). Later: [same-session comparisons #50](https://github.com/arcitai/factory/issues/50), [ZeroShot-style loops #97](https://github.com/arcitai/factory/issues/97), and [review quality #99](https://github.com/arcitai/factory/issues/99). General automation defaults and update ownership remain open choices. The trials retain R3's history loss, model stalls, R7's failed and interrupted review attempts and its two operator approvals, rc1's model transport failure and refused link removal, and the queue's recurring model-API "No response" failures; route evidence is limited ([#32](https://github.com/arcitai/factory/issues/32)) and account evidence remains under [#80](https://github.com/arcitai/factory/issues/80). They are qualification evidence, not unattended adoption. |
| Other factories | Adopt the reviewed method project by project through Foundation, after the Lab path works. |

The [qualification record](docs/qualification.md) separates source checks,
synthetic exercises and observed native operation. A published package does not
install a connection, isolate workers or establish unattended operation.
The [technical architecture notes](docs/architecture.md) explain those boundaries.

## Decisions and credit

The owner decides admission and delivery by default and may explicitly delegate
either for a defined scope. Keep that authority through continuation and workers;
raise genuinely new material scope or risk. See the
[operating policy](agent-ops/factory-agent-ops/references/policy.md).

Substantially inspired by Zach Lloyd's [Factory Stack](https://www.warp.dev/blog/the-factory-stack)
and [Warp Factories examples](https://github.com/warpdotdev/warp-factory-examples).
Warp supplies a platform and native execution engine; this independent method
assembles existing capabilities. It does not claim Warp schema compatibility.

Factory's method, code and documentation are MIT licensed. Arc’ It AI branding
has [separate terms](assets/branding/README.md). Third-party products and projects
retain their own terms.
