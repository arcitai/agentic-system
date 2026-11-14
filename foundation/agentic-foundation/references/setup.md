# Native setup and continuity

Revision: 0.2.1 · Updated: 2026-11-14

Use only the section needed for the requested host or project. This is preparation
and operating guidance, not a mandatory startup routine or a Foundation agent.
Preserve the owner’s tools, project work, instructions and history.

## 1. Choose the boundary

Select the native harness and execution environment the work needs. Scope access
by project and operation. A helper that must not have the project agent’s reach
needs a separately enforced environment; a worktree or fresh chat is not that
boundary. Existing project, service, network and broker grants survive a method
change unless separately changed under authority.

When credentials must stay unreadable to execution, keep their native broker
outside that boundary. Verify relevant allowed/refused operations, wrong-environment
access and revocation. Keep private details and secret values out of shared docs.
See [GitHub connections](github.md) and [authority and continuity](policy.md).

## Verify the effective account

Read the actual execution identity, configuration home, launch overrides, loaded
instructions/skills/plugins and imported account connections. Compare CLI settings
with actual task behavior. Do not assume a separate folder, profile or chat removes
inherited access. Preserve the human’s personal clients and unrelated projects.

## Select and stage a reviewed method

Use an immutable release or selected context-home revision. Staging copies files
but installs nothing:

```sh
python3 scripts/stage.py all --output /path/to/a-new-stage
```

Available groups are foundation, entry, evaluation and defence. Select only useful
methods. Inspect the resulting manifest and install through the harness’s supported
project/profile route; never overwrite local adaptations or existing files blindly.
Keep required resources with each skill. A name in instructions does not establish
discovery, loading or use. Reuse the [adoption record](adoption.md). A supported
plain instruction to read the selected policy by path can be the thin bootstrap;
an `@` line alone does not show that the harness expanded an import. An instruction
file changed during a running provider session may need an explicit reread or a
supported context/process reload. Verify the route the actual invocation received
and followed, preserving its existing native conversation and history.

## A persistent project conversation

Use an existing suitable conversation when it owns the context, keeping native
history and pending work. Choose the model with the owner and read back actual
model/effort. Pinning is a convenience, not a permanent role or permission grant.
The project agent can do the whole task and call bounded helpers when useful.
See [workspace guidance](workspace.md).

## The owner’s own AI agent

Optional agentic-entry helps an outside assistant understand the framework, find
the relevant project/version, and help with authorized starts or status. It need
not be installed in every project and is never a compulsory gateway. No separate
acceptance form is required where the current owner instruction already supplies
scope and authority. Entry retains no private cross-project queue.

## Keep the host ready after restart

Distinguish disk unlock, OS login, service startup, network reachability, client
pairing, task continuation and demonstrated useful work. Qualify what unattended
work actually depends on. A startup process, a restored socket or a retained chat
is not proof that a task resumed. Read actual native state before retrying uncertain
work; preserve original failures and history.

Use a selected native service manager and record recovery and updater ownership.
A shared-host update window has no active or unknown writers on the affected
surface. Preserve a recoverable starting state and verify affected operations and
boundaries afterwards. Do not stop unrelated projects or reboot just to update a
method. If power, network, login or decryption needs a human, say precisely what
that prevents; continue independent authorized work.

## T3 Code reference installation

T3 Code is optional. Beta is the desktop product label; stable is the selected
release channel. Prefer a single current stable client and a deliberately qualified
server version. Before removing an old client preserve its native data, saved
connections and history; move the application bundle reversibly, not its data.

A Mac operator client can connect to a Z13-hosted environment and show its native
project threads. Closing the client does not stop an independent host service.
Client, service and worker runtime versions are distinct facts. Upgrade only after
idle-state readback and a recoverable database/history copy; read back the same
project and conversation after migration, with relevant access and continuation proof.

For earlier platform commands and dated qualification examples, consult the
[historical T3 setup reference](historical-t3-setup-0.1.34.md) only as historical
material. Its AgentOps/ADLC startup instructions are superseded; do not reinstall
them. Recheck any command against the selected native version before reuse.
