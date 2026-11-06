# Technical architecture notes

Revision: 0.1.34 · Updated: 2026-11-06

The [public guide](https://gustavanderson.notion.site/Agentic-Systems-4046d2e17f568159a603de2dd6b91c2a)
owns the seven-layer overview, diagrams and human explanation. These notes cover
the repository's integration boundaries. [Source ownership](system-definition.md)
identifies the originals and versioned exports.

## Responsibilities

| Responsibility | Scope |
| --- | --- |
| Optional owner entry | Route requests to existing project leads and follow up bounded handoffs |
| Foundation | Prepare agent environment, project foundation and needed operating conditions |
| AgentOps | Lead one project within its mandate; assign work and coordinate review and delivery |
| Domain work | Apply the task method and checks for software, BI, defence, research or other work |
| Evaluation | Compare agreed outcomes and all-attempt quality, effort, time and available cost |
| Native tools and services | Execute agents, keep work/history and enforce actual settings and permissions |

A personal Planning Agent is optional. Explicitly delegated host maintenance may have an operator; this does not require
an additional coordinating model, global work queue or privileged project lead. See the
[host guide](../foundation/agentic-foundation/references/setup.md#keep-the-host-ready-after-restart).

## Three-level access architecture

The intended responsibilities are **owner → AgentOps → bounded workers**.
Assignments do not inherit the owner's or lead's credentials. Foundation prepares
and checks the actual boundary. Reviewers and evaluators are bounded workers.

For our Notion recipe, the lead is to use a connection limited to selected pages.
It supplies the chosen skills and task context to workers. A worktree or separate
chat separates work, but does not prevent access to shared credentials. Test the
allowed and refused operations through the actual selected tool and account.
Keep private installation facts and credentials out of this repository.

Each project lead needs a scoped execution boundary. In the current Lab, the
single AgentOps, pinned in the operator app, runs in its own environment on Z13
and creates and removes fresh per-task worker VMs through the native project
controller (bounded trials on 29–30 October 2026). The earlier prepared worker
environments were retired on 30 October 2026 and are no longer fallbacks;
unattended operation and the other open gaps remain
under [#32](https://github.com/arcitai/agentic-systems/issues/32). Explicitly trusted
related projects may share an environment and its access. All processes inside
one environment share that environment's service bindings; separate conversations
and worktrees do not isolate those credentials.

The owner's target is isolated, on-demand workers controlled by AgentOps inside
its own environment, with minimal actions on the physical host and no extra LLM
middleman. A prepared environment can host several fresh sessions when shared
access is acceptable; this is weaker than one fresh sandbox per agent. The current
T3 link starts tasks in existing environments, not new Docker microVMs.
Guest-local Docker can create containers, but that alone does not establish
per-worker network, credential or kernel isolation. Automatic provisioning,
cleanup and the chosen boundary still need qualification in [#32](https://github.com/arcitai/agentic-systems/issues/32).

## Native configuration and execution

The YAML original describes composition and links to methods. AgentOps interprets
it. Actual tool settings, OS/environment controls, mounts, network rules, service
permissions and repository protections enforce only what they configure.
`AGENTS.md` provides project instructions and routes; it grants no access.

T3 Code is the reference workspace; another capable native setup is valid. Read
current installed capabilities separately from released upstream functions and
dated historical observations. The host guide's Nightly examples keep their
original dates and are not current stable installation commands. The live native
roadmap remains [#32](https://github.com/arcitai/agentic-systems/issues/32), and the held
host adoption path remains [#34](https://github.com/arcitai/agentic-systems/issues/34).
Package source, actual installation changes and remaining holds are recorded separately.

Where enforced separation is needed, compare supported isolation choices against
the full execution environment, including any workspace server's own tools.
Qualify the selected container/VM or native boundary for the task. Agentic Systems adds no
bridge, approval pump, orchestrator or policy engine to fill a native-tool gap.

## Results, learning and experiments

Project artifacts, task status, logs and usage retain their native sources. Keep
accepted decisions and reusable lessons in the relevant original; native memory
is working context. Model/provider choices and permitted data destinations belong
to the selected project's setup. A shared account or model name is not a policy.

For model comparisons, fork the same frozen session checkpoint into independent
attempts with the same input and task state, changing only the role/model under
test. Subsequent outputs may diverge. A transcript alone does not restore tools,
data, permissions or hidden provider state. Retain limitations and whole-attempt
results; see [replay #50](https://github.com/arcitai/agentic-systems/issues/50).

Source checks, a rehearsal, installed skills and qualified operation are different
claims. [Qualification](qualification.md) retains the dated evidence and remaining
live work. A released method does not prove automatic scheduling, worker isolation,
recovery, deployment or useful work in a new installation.
