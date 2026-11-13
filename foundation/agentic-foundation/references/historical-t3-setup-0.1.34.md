# Historical T3 setup reference

Revision: 0.2.0 · Updated: 2026-11-14

Superseded historical material from the 0.1.34 distribution. Its original text and observation dates follow unchanged; do not apply its AgentOps/ADLC startup defaults to the current method. Use setup.md for current guidance.

---

# Set up the host and operator client

Revision: 0.1.31 · Updated: 2026-10-30

This reference setup uses T3 Code on a Linux execution host, with a Mac and
optionally a phone as clients. The host can be a laptop, workstation or VPS.
The method itself also works without T3 after qualifying
the chosen harness's discovery and operation.

Reference version: T3 **0.0.46-nightly.20261009.2873**; upstream setup guidance
checked 2026-10-09. This is a prerelease qualification baseline, not a guarantee
for every host or future Nightly. Keep the selected client/server/provider versions
and observed proof in the installation record. Native delegation and automation
need their own qualification; installing them does not authorize their use.
See [upstream installation](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/install.md).

Prefer the official stable channel as the normal baseline. Use a Nightly only for
a concrete capability reason, with its own qualification. The commands and
observations below stay at Nightly 2873, where they were qualified. For a stable
release, follow its own installation and update documentation, check its bytes,
migration path and supported client/server combination, and qualify it like any
other version. Move an existing host to it only through that host's own recovery
and maintenance process; a newer release does not bypass that process's open
gates. A cutover is verified only when the intended server and every client read
back both the exact version and the stable channel; a desktop update or a request
for one version is not that readback. A combined update action can update
providers, servers and connected machines together, so it is not a scoped version
check. Documentation of a newer launcher's rollback does not show that an older
installation has that launcher or its guarantees.

Keep three things apart: features in the installed T3, upstream work that is
released but not yet installed or proposed but unmerged, and boundaries the
installation actually enforces. A released fix is not installed, and an installed
one is not accepted until it works in this installation. For the Agentic Systems host,
[#34](https://github.com/arcitai/agentic-systems/issues/34) holds the selected stable target
and its maintenance gates, and [#32](https://github.com/arcitai/agentic-systems/issues/32)
holds the live roadmap of released and pending native functions. Read those issues
for current status rather than copying it here. Agentic Systems adds no runtime, approval
service or bridge for a function still pending upstream; it waits for the official
release and qualifies it.

Stable T3 source documents an outside-agent route over MCP with OAuth, which an
owner-side caller could use to read, start, message and stop threads within a
chosen writable mode. That mode covers all of the environment's projects. It is
not a per-project access list, it grants no authority to decide another worker's
approval, and it is no isolation boundary. Treat it as documented source only
until it is connected and qualified in the installation; a qualified native route
like this is preferable to a custom bridge.

Start by identifying the existing project/adoption record. Use
[the adoption guidance](adoption.md#persistent-choices-and-exceptions) to establish
relevant persistent choices and separate intent, native application scope and
dated verification. Reuse its choice families, safe repository policy and private
installation record; do not create another inventory. For authorized changes,
follow its effective-state readback, scope, application and verification steps.
Hand ongoing upkeep for the current project to AgentOps within its mandate.

## 1. Choose the boundary

Use an ordinary execution account on the host, with access to the selected repos
and tools. On a shared personal machine, give the agents a separate boundary with
its own unprivileged account: a VM or a rootless container, selected only after the
comparison below. Keep the personal home, SSH agent, browser, clipboard and host
sockets outside it; admit shared folders/devices only for a stated need.
On a dedicated host, a separate unprivileged OS user may be sufficient for the
selected workload. It shares the kernel and is not equivalent to a VM.
Keep deployment/admin credentials outside implementation workers unless a task
explicitly needs them. A second T3 project or provider config directory under the
same OS user is not a filesystem sandbox.

When a stronger boundary is needed, compare a **rootless container** and a **VM**
against the same requirements before selecting either. A rootless container shares
the host kernel; a VM runs its own guest kernel. Neither is qualified merely by
starting it. Put the whole execution environment inside the boundary: the T3
server and the host-side tools it runs, not just a provider executable, because a
wrapped provider leaves other effectful tools outside it. Compare:

| Requirement | Check in each candidate |
| --- | --- |
| Identity and credentials | Only the selected workspace, identity and least-privilege credentials; no inherited owner home, personal connectors, browser profile, SSH agent, privileged or runtime socket, or unrelated project access |
| Workspaces | The author reaches its selected checkout; an independent reviewer reaches the immutable candidate with allocated scratch output; shared Git metadata does not expose unrelated repositories |
| Allowed and refused actions | Real file, symlink, process, network, socket and remote-tool operations, tested separately for Codex and Claude; harness sandboxing and account-synced connectors are separate checks |
| Native operation | Environment connection, provider login, delegation and approvals still work inside, with any callback or localhost reachability recorded and no broad host-network or credential escape |
| Recovery and cost | Disconnect, restart, recovery, cleanup and revoked grants actually verified, plus the maintenance and configuration effort |

The reusable method requires no separate browser. If a task needs a browser, its
actual profile, session and access must fit the chosen boundary. Run such a
comparison only on disposable inputs in a separately prepared test area, with its
operator, allowed effects and recovery agreed; keep an unavailable check open. The
Agentic Systems comparison and its decision are tracked in
[#32](https://github.com/arcitai/agentic-systems/issues/32). A Cloudflare-based approach
remains optional research in [#79](https://github.com/arcitai/agentic-systems/issues/79),
not a third required boundary.

Use one persistent AgentOps thread in the owner's existing project when it has the
right context and access. A separate lead project is optional, not a requirement.
Activate the lead role in that thread; preserve the project's shared instructions.
Workers receive the target project's context and skills. Separate provider profiles,
T3 environments/OS identities, VMs or containers are appropriate when
the lead, workers or projects require different filesystem/network trust.

The Lab's target is one isolated, on-demand sandbox per agent, created and removed
by AgentOps inside its own environment, with minimal physical-host actions and no
extra coordinating model. In bounded trials (R7 on 29 October 2026; rc1 on Stable
0.1.5 in Auto on 30 October 2026), the lead created and removed fresh per-task
worker VMs through the native project controller. The prepared baseline worker
environments were retired on 30 October 2026 (stopped; disks and verified history
copies retained, not a clean-stop qualification) and are no longer fallbacks. Unattended
intake, approval-free operation, account-wide isolation, boot/login startup,
updates and GUI/new-VM restore remain unqualified and tracked in
[#32](https://github.com/arcitai/agentic-systems/issues/32). These are Lab recipe choices;
adopting projects select a boundary that enforces their actual requirements.
Trusted related projects may explicitly share an environment and its access.
Use one native GUI to follow projects, threads and results.
An operator-assisted relay between servers does not prove automatic delegation.
Prefer stable; qualify an official Nightly when a needed capability is absent
from stable, and record the exact limitation/version in the installation and issue.
Do not build a replacement orchestration engine.

Several fresh sessions may share an environment only as an explicitly accepted,
weaker arrangement. Separate worktrees protect concurrent changes, not credentials.
Foundation prepares and qualifies only the sandbox capability the work needs;
AgentOps uses the accepted capability for its tasks. Record who can create,
start and stop sandboxes, whether stopped environments retain history, and which
actions are actually automatic. Native T3 delegation to a prepared environment
does not provision a VM; in the Lab, AgentOps creates a worker VM through the
native project controller before delegating to it. Qualify on-demand creation and
idle shutdown separately; do not grant host administration to workers to make it
appear autonomous. Pin only the persistent AgentOps lead; workers stay unpinned.

Keep the owner's personal context and Agentic Systems execution context separate. Do not
copy a personal method installation, provider home, Notion workspace, browser
profile or credentials into the execution account. Record only the relevant
identity and private source routes in the existing installation record.

Preserve any old Agentic Systems runtime and private history while qualifying this setup.
Avoid pointing two active agent writers at the same checkout. Do not run native
services as root. Keep the host powered, awake and network-accessible.

### Verify the effective account

Resolve the actual execution host, OS/service user, provider account and
organization, native configuration home, launch route and applicable project or
session overrides. Model authentication and permission to use company or personal
systems are separate capabilities.

Inspect loaded user/project instructions, personal-context pointers, skills,
plugins and effective tools, including connectors imported from the provider
account. A separate user or empty configuration directory does not establish
their absence. Distinguish files on disk, CLI inventory and the tools exposed in
a fresh actual worker through the selected T3 or other harness route.

Compare that worker's capabilities with its assigned scope. Where a correction
is needed, verify a supported control for that exact route/version. Confirm that
the installed version recognizes the setting; an unknown key is not a control.
Apply it only within the authorized scope, then check required presence and
unwanted absence in a fresh worker. Preserve unrelated settings, the owner's
personal connectors, GitHub access and native orchestration. Record the personal-client preservation
check separately; an unavailable check stays a gap. Do not revoke or broaden
account-wide access to make the result pass.

Claude Code documentation checked 2026-10-29 says `disableClaudeAiConnectors: true`
controls connectors fetched by CLI/SDK sessions. It does not control connectors
delivered by the desktop app's local/SSH sessions, or explicitly supplied MCP
servers. An inference-only `claude setup-token` login does not fetch account
connectors; their absence there does not demonstrate that an exclusion setting
worked. Verify the selected route rather than applying this example universally.
See [Claude's connector delivery and controls](https://code.claude.com/docs/en/mcp#how-connectors-reach-claude-code).

Record active sessions that retain an older tool registry; move affected work at
a safe checkpoint rather than silently interrupting it. Recheck the affected
boundary after relevant account/organization, connector, instruction, configuration
or harness changes. Reuse unchanged proof instead of repeating the full check on
every small task. See the [installation context](adoption.md#relevant-installation-context)
for the retained evidence and remaining gaps.

## Least privilege in practice

Start AgentOps and ADLC workers on the same restricted baseline when that meets
the intended trust boundary. AgentOps has more coordination responsibility, not
blanket root, unrestricted network or deployment access. Keep the service account
out of sudo/admin and host-control groups. Use task-specific GitHub/deployment
access where available; native tool approval does not shrink a token's permissions.

| Control | Configure and prove | Limit |
| --- | --- | --- |
| Host account | Unprivileged account; personal home, admin credentials and host sockets inaccessible; prove an allowed operation and a refused one | Same-account processes and projects still share accessible resources |
| T3 mode | Begin with supervised for read-only assessment; for accepted editing, choose and read back the mode per provider and task | Each mode maps to a different provider policy; Auto is an approval policy, not one universal sandbox |
| Codex | In this T3 baseline, Auto maps to workspace-write with on-request approval and native auto-review; supervised maps to read-only | T3 supplies the runtime policy; a CLI configuration default alone does not prove the T3 turn uses it. Measure its boundary separately from Claude's |
| Claude | Enable native Bash sandboxing and the outside-read block in the selected profile; disable unsandboxed retries and fail if sandboxing is unavailable; qualify Auto-accept edits where outside file edits must wait for approval; prove each in an actual T3-launched turn | Bash sandboxing does not enclose file tools, MCP servers or hooks. The read block does not stop writes, and in Auto outside native edits were not held |
| GitHub / delivery | Read effective repository, Projects and workflow permissions; use narrower credentials or a separate delivery identity where needed | A shared login remains shared access, even when commits credit several agents |

For a selected Claude profile on a supported host, this is a minimal configuration
to merge deliberately into its existing settings, not overwrite them. The read
block requires Claude Code 2.1.257 or later:

```json
{
  "permissions": {
    "blockReadsOutsideWorkingDirectories": true
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}
```

Install the native dependencies first. Check which setting sources and working
directories the T3/SDK launch actually uses; CLI and SDK defaults can differ, and
a launch that loads only user settings ignores a project-local file. Start a new
session after a change. Test a permitted workspace write and a denied write to a
disposable path outside it, without retrying outside the sandbox. Then test native
Read, Edit and Write inside and outside the workspace, plus required network
destinations and MCP operations. A terminal probe or a present settings file is
not a passing T3 integration test. Keep configured and demonstrated controls separate.

In this T3 baseline, Auto maps to Claude's `auto` mode and Auto-accept edits to
`acceptEdits` with T3's approval callback. In a qualified launch with the read
block, Auto still let native Edit and Write change files outside the workspace.
When outside file edits must wait for a person, qualify Auto-accept edits for that
Claude worker: workspace edits proceed, while outside edits, many shell commands
and explicit reads of installed skills can each ask for approval. Budget that
attention; keep a declined operation declined rather than retrying it through
another tool. This is assisted operation with user-editable guardrails, not
unattended throughput, an unbypassable policy or role/process isolation.

Native sandbox defaults may allow broad reads. Keep credentials outside the
agent's accessible environment where possible, and use native read-deny/credential
controls for selected secrets. User-editable settings are a guardrail, not an
administrator-enforced policy. For non-bypassable restrictions, use managed native
policy controlled outside the agent's identity, plus OS/remote-service enforcement.
Do not install a machine-wide policy blindly on a shared personal host.

**To add access:** name the operation and target, choose the smallest native grant
(path, domain, tool, repository or deployment environment), identify who authorizes
it, and set its duration or removal condition. Apply at the appropriate control,
read it back, and prove the required operation while an unrelated operation still
fails. Remove temporary grants afterward and verify revocation; a recorded expiry
does not revoke access. Avoid changing every thread to Full
access to resolve one denied build command. If AgentOps needs access that workers
must not possess, use separate identities/environments; a title is not an ACL.

Sources: [T3 permission modes](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/permission-modes.md),
[T3 Claude mode mapping](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts#L1511-L1603),
[Codex permissions](https://learn.chatgpt.com/docs/permissions),
[Claude permission modes](https://code.claude.com/docs/en/permissions),
[Claude read restriction](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories),
[Claude sandbox scope and enforcement](https://code.claude.com/docs/en/sandboxing).

## 2. Install and authenticate on the execution host

Install Git, the GitHub CLI and the native provider CLIs using their supported
instructions. Prefer a maintained native installation owned by the execution user
for provider CLIs. Point T3 at its stable launcher, not a copied versioned binary
under an administrator-owned directory; copied binaries can break native updater
detection. Keep provider profiles and credentials unchanged when repairing paths. Inspect versions and authenticate the intended execution account.
Repository and Project operations need appropriate GitHub access; deployment
credentials are a separate decision. Follow the
[GitHub connection checks](github.md#qualify-the-connection) for CLI, Git and
Project access on that same account and the native T3 readback.

Install a selected T3 release using its official installer. For the documented
baseline, download and inspect the script before executing it:

```sh
factory_install_dir="$(mktemp -d)" &&
  curl -fsSLo "$factory_install_dir/install.sh" https://t3.codes/install.sh &&
  less "$factory_install_dir/install.sh"
```

After reviewing that downloaded script, execute the same file:

```sh
T3CODE_CHANNEL=nightly T3CODE_VERSION=0.0.46-nightly.20261009.2873 sh "${factory_install_dir:?Use the directory from the successful download and review above}/install.sh"
```

Use the installer-reported binary path if `~/.local/bin` is not on `PATH`.
Check `t3 --version`, `codex --version`, `claude --version`, `git --version`
and `gh --version` as the account that will run the service.
Stop and reconcile if the reported T3 version differs from the selected version.
Select the official Nightly release, not a maintainer's `preview` build. Keep all
clients on a compatible orchestration protocol and check the provider compatibility
reported for that release before starting agent work.

In T3's provider settings, choose separate Codex and Claude configuration
directories for this work. Authenticate against those same paths on the host:

```sh
factory_codex_profile="$HOME/.local/share/agentic-system-profiles/codex"
factory_claude_profile="$HOME/.local/share/agentic-system-profiles/claude"
mkdir -p "$factory_codex_profile" "$factory_claude_profile"
chmod 700 "$factory_codex_profile" "$factory_claude_profile"
CODEX_HOME="$factory_codex_profile" codex login
CLAUDE_CONFIG_DIR="$factory_claude_profile" claude auth login
```

Open the provider's login link in the browser you use, complete authentication,
and finish any native callback on the execution host. The browser may be on the
host or another machine. Keep codes and credentials out of issues and docs.
Use the provider's documented remote/device-login route if its callback requires it.
Verify the account in T3; a browser login alone does not prove the CLI profile is
authenticated. Existing dedicated profiles may be reused deliberately without
copying their credentials into a new location.

Start with Codex and Claude if those are the selected subscriptions. Choose models
from the actual provider catalog; use the owner's selection and measured results.
Extra providers and automatic model routing are optional. Read usage and limits
as described in [Usage and limits](#usage-and-limits).

References: [Codex profiles](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/providers-codex.md),
[Claude profiles and skills](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/providers-claude.md).

### Usage and limits

Assessed against T3 upstream `d83929ad`, 2026-10-15; read back the installed
client's view before relying on it.

Open **Usage** from the sidebar or command palette (`mod+U` when the terminal is
not focused). Cost and Tokens show history over a 24 h, 7 d, 30 d or 90 d window;
Limits shows each provider's own reset windows; the history-period controls are disabled there.
Choose the environment (default: all) and inspect the provider/model breakdown and
visibility each tab supports. These selections are local view preferences; they
configure no billing, permission, quota or security policy.

- Usage scans each configured provider's native history, including work outside
  T3 and disabled accounts. Sources sharing one provider home, such as one
  `CODEX_HOME` or `CLAUDE_CONFIG_DIR`, count once; use that deduplication rather
  than adding totals across environments.
- In the assessed pin, Usage has no project or thread attribution, and an
  environment filter does not infer one. Do not estimate project cost retrospectively.
  As of 2026-10-15 native project accounting is an open upstream
  [proposal](https://github.com/pingdotgg/t3code/discussions/16722) and
  [unmerged PR](https://github.com/pingdotgg/t3code/pull/15902); do not treat it as
  installed, and recheck after a supported update.
- Tokens are recorded units; reasoning is part of output, so do not add it twice.
- Cost is an API-equivalent estimate where provider-reported or model-priced, not a
  subscription charge; unpriced usage has no cost figure. Use the provider for actual
  plans and charges: [Codex](https://learn.chatgpt.com/docs/pricing),
  [Claude](https://code.claude.com/docs/en/costs).
- Limits and resets belong to the provider account, not a project. One account used
  by several environments is one allowance; do not sum it. `/usage-limits` reads
  cached limits without starting a turn; refresh through the existing control.
- Missing history, a stale scan or unavailable pricing or limits is unknown, not zero.

Do not activate banked resets or paid overage, switch accounts or configure prices
to produce a figure.

A machine is the OS host; a server is the running T3 backend; an environment is
that backend's identity, data and auth scope; a saved connection is one route to it;
a project groups a repository or workspace; a provider account holds subscription,
billing, history and authentication. Several environments on one host can have
separate IDs, data and connection grants, yet still share the OS user and provider
homes. Projects are not filesystem sandboxes: `filesystem:read` reaches what the
server's OS user can read ([environment auth](https://github.com/pingdotgg/t3code/blob/d83929ad0bb0d4aec800f12c332de57e873cc7e5/docs/internals/environment-auth.md)).
Keep the existing environment rather than adding one per project for accounting or
isolation. Where a task genuinely needs separation, qualify a separate OS identity
or protected native boundary as in [Choose the boundary](#1-choose-the-boundary);
remaining approval and worker-boundary limits are tracked in
[Agentic Systems #32](https://github.com/arcitai/agentic-systems/issues/32) and
[#33](https://github.com/arcitai/agentic-systems/issues/33).

Sources: [T3 usage](https://github.com/pingdotgg/t3code/blob/d83929ad0bb0d4aec800f12c332de57e873cc7e5/docs/user/usage.md),
[usage contract](https://github.com/pingdotgg/t3code/blob/d83929ad0bb0d4aec800f12c332de57e873cc7e5/packages/contracts/src/usage.ts).

## 3. Make the service independent of the client

On the host, as its execution user:

```sh
t3 service install
t3 service status
```

Linux uses a systemd user service. Confirm the service is running, enabled and
able to survive logout. If setup reports that lingering needs an administrator,
complete only the reported host-administration step with that administrator.
Do not solve it by granting the worker unrestricted sudo.

Use T3 Connect or the supported direct/private-network connection to the already
running service. Do not assume a server started and managed by a desktop SSH
connection survives closing that client. Qualify the selected route under load
and reconnection: [known shutdown/reconnect report](https://github.com/pingdotgg/t3code/issues/15608).
Inspect service ownership before mixing multiple launch methods.

Before an update or restart, read active work and arrange interruption/recovery.
Pin versions for a qualification run. Stop the service and privately back up its
`userdata`, service configuration and prior version before a major migration.
The backup contains credentials and history; keep it with restricted access on
the execution host. Restart the service after the consistent backup, then use the
native update path, for example:

```sh
t3 update 0.0.46-nightly.20261009.2873 --channel nightly
```

The restart interrupts active turns. V2 copies `state.sqlite` to `statev2.sqlite`
once, preserving the V1 database. Later activity in the two versions does not
sync. Messages and thread metadata migrate; live provider sessions, old tool
activity, approvals and checkpoints do not. The first continued turn must reload
instructions, skills and outstanding decisions. Preserve the recovery copy;
inspect it read-only if needed. A binary downgrade alone is not a data rollback.

Upgrade every operator client to a compatible V2 build, then verify the service,
connection route, projects, pins, archives, transcripts and a harmless provider
turn. Record missing history or changed behavior before restarting real work.
[Updating](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/updating.md),
[V2 migration and backup](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/thread-migration.md).

### Telemetry opt-out

When this recipe uses T3 Code and Claude Code, the execution host opts out of
their telemetry unless a project records an authorized exception in its own
persistent-choice record. A telemetry-on exception names the egress it allows;
it does not silently widen network access. Both products stay replaceable; this
says nothing about other harnesses. It covers the host's T3 service and the
Claude processes it starts, including worker sandboxes; operator clients are
outside it and unverified (the T3 desktop app, including its Local environment,
reads the variable from the Mac's shell profile, and the phone app's crash
reports have their own Diagnostics setting).

For T3 0.1.5, set `T3CODE_TELEMETRY_ENABLED=false` in the T3 server environment
before it starts. T3 documents that this stops product events and relay tracing.
For Claude Code, set `DISABLE_TELEMETRY` to a nonempty value, such as `1`, in the
Claude process environment. Cover the lead and every worker sandbox through the
native environment mechanism, such as the service environment or a sandbox's
create-time environment. Never pass secrets that way. Keep the model and
permission mode explicit: telemetry off changes Claude's default mode for
sessions that set none.

Verify the effect instead of assuming it. After the restart and at least one
turn, Claude's system/init message in the T3 provider event log should report
`analytics_disabled: true`. The server trace in the T3 userdata `logs/` directory
should show `AnalyticsService.record` spans but no `AnalyticsService.sendBatch`
attempt and no `ingest.t3.codes` request. Where possible, compare with a
pre-change trace or an unflagged control that did show them. Keep local history
and usage records. This is not zero egress and does not change provider data
retention. OpenTelemetry relay tracing was not separately observed. On Claude
2.1.306, effects on error reports, feature flags, Monitor and idle compaction are
unverified. T3 relay diagnostics are lost. Vendor behaviour can change with
versions; re-verify after each T3 or Claude upgrade.

Sources: [T3 telemetry](https://github.com/pingdotgg/t3code/blob/v0.1.5/docs/user/telemetry.md),
[T3 analytics delivery](https://github.com/pingdotgg/t3code/blob/v0.1.5/apps/server/src/telemetry/AnalyticsService.ts),
[Claude Code changelog](https://github.com/anthropics/claude-code/blob/b3f291d131924810e2b7713ededc144843a229d5/CHANGELOG.md)
(2.1.283–2.1.314); dated Lab evidence in [#108](https://github.com/arcitai/agentic-systems/issues/108).

## 4. Connect the operator clients

Install the matching T3 desktop release on the Mac. Use **Settings → Connections**
to connect to the host and verify the displayed execution environment before
starting work. Provider logins, tools, repos and worktrees for remote tasks belong
on the host. The Mac does not need another set of worker credentials for those tasks.

A desktop app running on the host is also a client. If it runs as a different
OS user, connect it to the existing execution service rather than importing the
same repositories into that user's local environment. Use native pairing to its
reachable endpoint; on the same host this can be the service's loopback address.
For a saved SSH environment, verify that it attaches to this independent service
instead of starting a desktop-managed server. Check service ownership and process
identity, then prove a bounded task survives closing the client and is readable
after reconnect. If service reuse is not established, use Connect or supported
direct/private-network pairing to the existing service. Verify both clients show
the same project and thread history, not two independent copies.

**Local environment** controls the extra backend managed by that desktop client.
For a client used only to access the execution service, turn it off under
**Settings → Connections**, using T3's native restart confirmation. First reconcile
any local work and confirm the saved service connection. This does not stop the
independent systemd service, even when the client is on the host itself. Keep it
on if local work is also intended. Local history and remote connections are retained.
After restart, check the toggle, Connected status and the same thread; check that
the execution service remained active. Avoid manually editing T3's database.

Check the permissions of the route actually in use; saved routes can have different
sessions and grants. A migrated connection notice does not authorize broader access.

Pairing links are credentials. Transfer them directly into the intended client,
then verify readback and remove temporary copies. If typing a full link fails,
use the dialog's separate Host and Pairing code fields. Reconcile an uncertain
pairing before creating another. Do not import a personal browser profile to solve
an execution-host login, or infer GitHub CLI access from a browser session.

T3 Connect links environments through its native account flow, including headless
hosts. When Connect and mobile notifications are selected, a headless host with
an existing service can use the following as its execution account. Reconcile
active runs and known background work before the restart:

```sh
t3 connect link --headless
t3 connect publish
t3 service restart
t3 connect status
```

Complete the account login and native relay-client installation prompts. Linking
finishes asynchronously after the service starts; saved authorization alone is
not reachability. Reuse that service rather than starting another server. Sign
in to the same T3 account on each client. Add Connect as a route to the existing
environment and inspect the route actually in use; retained SSH/direct routes
can provide fallback. If a newly linked environment is absent from a client that
was already open, refresh its view before trying to pair again.

Direct/Tailscale connections are alternatives for access. Background phone
push requires T3 Connect; the phone app is T3 Code, not the existing Codex/ChatGPT
conversation. Test a real question/approval from the phone before relying on it.
Select notification preferences deliberately. Keep external integrations for a
later qualified route.

In the pinned historical baseline, Nightly V2 requires the **beta mobile app**; the stable store apps cannot connect
to this baseline. Use the beta links in T3's **Settings → General → Mobile app**
and prove the actual phone question/response route before relying on it.

[Connections](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/remote-access.md),
[mobile notifications](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/mobile-notifications.md).

## Keep the host ready after restart

An installation can look ready while the operator's apps do not start after login
and no maintenance schedule is active. The installer or host owner establishes and
verifies the chosen startup, service, power, network and schedule settings.

An installation may also choose an owner-side **host coordinator**, sometimes
called a Planning Agent: a thread with an explicit mandate to keep the host
continuous, coordinate maintenance that affects several projects, and ask
Foundation to repair a host condition. It is optional. An existing lead thread can
take that mandate, so no extra top-level chat, daemon or central queue is needed.
It does not replace each project's AgentOps, which keeps that product's priorities,
workers and acceptance, and ADLC still performs the tasks. The role grants no
administrator rights or personal connectors; host administration stays with the
person or narrow native route that holds it. Resolve the actual host and accounts,
client and server routes, effective permissions, and the person who can operate
recovery when the service is down. After a restart or migration, reuse the
existing coordinator and leads instead of starting replacements.

Each startup stage is a separate observation:

| Stage | Establish and verify | Limit |
| --- | --- | --- |
| Disk unlock | Who unlocks an encrypted disk after boot, and how they learn it is waiting | Nothing below starts until then |
| Headless service boot | The execution service is enabled, starts at boot without a login and survives logout, as in [section 3](#3-make-the-service-independent-of-the-client) | Read it back after boot; the install command alone is not proof |
| Network routes | The network, a private route such as Tailscale, T3 Connect and the chosen SSH route come up without a desktop login | A client may reconnect through a fallback route rather than the selected one |
| Desktop session | Operator apps the owner expects start through the desktop's supported autostart after login | Runs only after someone logs in; it is not service boot |
| Power and reachability | On external power the host stays awake and reachable with the screen locked; battery protection and suspend follow the owner's choice | Locked operation on power is not battery or suspend recovery |

Prove readiness at each boundary separately: boot, login, client disconnect and
reconnect, and an actual scheduled wake. After a controlled reboot, read back from
a fresh native turn that the service, routes, projects, threads and held decisions
are present, and that the expected apps started after login. One scheduled wake is
not reboot, disconnected-client or full recovery proof. Notify someone when a stage
fails or holds, a gap appears or maintenance changed something; do not send daily
unchanged pings.

Hand each relevant capability over in the existing adoption record, without a new
template: the selected capability; its actual native owner and control, applied
scope and readback; where its private evidence lives and who holds it; and the
exact remaining gap and next action. A missing access, recovery or launcher fact
stays a named capability gap. Keep host identities, paths, raw history and recovery
copies private.

## 5. Adopt selected skills

Clone a reviewed Agentic Systems tag on the host into a source directory, separate from
the application. From that checkout, run the staging helper for each needed bundle:

```sh
factory_stage_root="$(mktemp -d)" &&
  python3 scripts/stage.py foundation --output "$factory_stage_root/foundation" &&
  python3 scripts/stage.py agent-ops --output "$factory_stage_root/agent-ops" &&
  python3 scripts/stage.py adlc --output "$factory_stage_root/adlc"
```

Select scope deliberately:

| Bundle | Destination |
| --- | --- |
| Foundation | The setup/operator context; not needed by every implementation worker |
| Agent Ops | The selected project, activated in its Ops thread; use a separate project/profile/identity when its access needs differ |
| ADLC | The application project, or the native user/config scope described below |

To stage every canonical skill as one flat set with one manifest, run
`python3 scripts/stage.py all --output "$factory_stage_root/all"`. It refuses a
missing group or a duplicate skill name, and keeps the same tracked-only, symlink
and fresh-destination controls. Copy from it only the skills each destination needs.

For Codex, use the native project location `.agents/skills/`. Its documented user
location is `$HOME/.agents/skills`, shared across that OS user's projects; changing
`CODEX_HOME` alone does not isolate that skill location. A project skill is discoverable
by other threads in that project; discovery is not assignment of the lead role.
Use a separate project or OS identity when discovery or access must be exclusive.
See [native Codex discovery](https://learn.chatgpt.com/docs/build-skills).
For Claude, T3 reads the project's `.claude/skills/`
and the selected config directory's `skills/`; the config copy wins on a name clash.
Prefer project scope. Copy a reviewed complete skill folder from the stage into
the chosen location, including its references and license. Refuse an existing
same-name destination until you have reviewed the differences; do not blindly merge
or overwrite it. Keep separate installed copies only where the harness requires
them, derived from the same reviewed source. Do not maintain two edited originals.

For application worktrees, commit the selected project skills through that
application's normal review process so new worktrees contain them. If the project
should not track skills, use a deliberately chosen native user/config scope
with the sharing boundary described above; verify it in the selected harness. Never
assume an untracked copy in one checkout exists in another worktree. Verify native
discovery in an actual new worktree before delegating to it.

After reviewing the selected source and bundle, this example stages a fresh
copy and adopts it into the selected existing Codex project. Replace the example
path with the inspected workspace and run it from the Agentic Systems source checkout:

```sh
factory_lead_project="$HOME/Developer/your-project"
factory_lead_stage="$(mktemp -d)" &&
  python3 scripts/stage.py agent-ops --output "$factory_lead_stage/bundle" &&
  mkdir -p "$factory_lead_project/.agents/skills" &&
  test ! -e "$factory_lead_project/.agents/skills/agentic-agent-ops" &&
  test ! -L "$factory_lead_project/.agents/skills/agentic-agent-ops" &&
  cp -R "$factory_lead_stage/bundle/skills/agentic-agent-ops" "$factory_lead_project/.agents/skills/"
```

Read the destination and compare it with the stage manifest. An existing folder
requires deliberate reconciliation; failure of the command is not successful adoption.
Before removing the temporary stage, retain its `manifest.json` in the persistent
private adoption record, alongside the version, date and installed destination.
The manifest is at the bundle root, not inside the copied skill directory.
Use `.claude/skills` instead for a project-scoped Claude installation. In the
intended harness and session, verify the correct skills appear and can read their
references. Ask it to assess a harmless example; copied files alone are not
discovery proof.
Do not replace the application's AGENTS/CLAUDE instructions. Add a short route only
where the native harness requires one, preserving the canonical source.

In the Agentic Systems method repository itself, the Ops thread can read the reviewed
canonical skill files directly without copying them back into their own source
tree. Record this as explicit source loading, not native skill discovery. Configure
the persistent thread with [the operator workspace guide](workspace.md).

### The owner's own AI agent

The owner's everyday AI agent reaches Agentic Systems through `agentic-entry`. It routes
each request to the right existing project lead, and loads `agentic-foundation`
when the owner asks to set up or explain a host. Install both from the all-set
stage into that agent's own native skill scope, such as its user-level skill
location. Project leads keep their own installations. Keep the owner's agent and
personal connectors out of the execution account, as in
[Choose the boundary](#1-choose-the-boundary).

Record four separate states in the adoption record:

- **Requested:** the owner asked for the entry in a named agent and harness.
- **Installed:** the destination and the retained stage manifest.
- **Discovered:** a readback from the actual caller surface showing the skill is
  listed or can be invoked.
- **Used:** a real request routed through it to the intended lead.

Do not assume a client picks up a newly installed skill in a running session, or
that it needs a restart; read it back in the intended harness and session. If
the skill cannot be discovered, the agent may read the canonical file explicitly
from a reviewed checkout; record that as explicit loading. An inaccessible path is
a gap to report, not a reason to widen access.

Agentic Systems ships portable canonical skills and this staging route. Codex documents
[plugins](https://developers.openai.com/plugins/build/plugins) as a distribution
unit for several skills, alongside [repository and user skills](https://learn.chatgpt.com/docs/build-skills).
Claude has its own [skill locations and invocation](https://code.claude.com/docs/en/skills).
A Codex plugin is not proof of T3 or Claude discovery. A plugin remains an optional
later packaging for a harness that needs one; none is delivered or installed here.

To update, stage the new reviewed tag, compare it with the installed copy and its
retained manifest, then adopt it deliberately. To roll back, restore the prior
reviewed copy named by its manifest, as in [Removal and recovery](#removal-and-recovery).

## 6. Prepare the repo and prove one delivery

Follow [repository preparation](github.md). Record the two decision points,
delegation, checks and delivery boundary using [the adoption outline](adoption.md).
Start with one bounded real task; prove implementation, independent review, a
review finding/fix and the authorized delivery. Then exercise client disconnect,
reconnect, permission refusal, unavailable provider and recovery without duplicates.

Add autonomous backlog scheduling or GitHub webhooks only after selecting the
supported native capability and qualifying its sender, authority, duplicates and
offline behavior. Native schedules are version-specific. A GitHub issue alone
does not wake the stable baseline or grant implementation access.

## Updates and host maintenance

Use the installed tools' native update paths. Record the selected channel,
responsible operator, interruption/recovery rules and last actual result in the
private installation record. Checking for updates, installing them and proving
compatibility are different actions.

| Component | Native route | Boundary |
| --- | --- | --- |
| Desktop/mobile clients | Official application updater or store/beta channel | Match the host's protocol; an updated client does not update the server |
| T3 background server | The named environment's Update server action or `t3 update <selected-version>` | Reconcile active turns and background commands first; it restarts the service. Read back both version and channel; a service keeps its current channel |
| Claude native installation | Native background updates; `claude doctor` reports installation, channel and updater state | New version takes effect on the next process; custom/copied launchers may prevent adoption |
| Codex | Native installation/update support, or T3's detected provider update action | Inspect the actual installation; do not infer automatic installation merely from a version-check setting |
| Linux/Omarchy | Distribution's maintained update command and notifications | Package changes, migrations, prompts and reboot are system administration; a check notification is not an unattended update |
| Agentic Systems skills | Reviewed tag → staged diff → checks → deliberate adoption | Preserve local adaptations and verify discovery; do not auto-overwrite project instructions |
| Optional method package, such as OSM | The package owner's qualified native route, as in [migrating an optional method](method-migration.md) | Agentic Systems does not depend on it; preserve its context home, IDs and standing calls |

Native update checks may stay enabled. Automatically applying updates requires a
selected, supported and tested maintenance route: idle-work checks, bounded scope,
recovery, readback and an actionable failure signal. Do not add an Agentic Systems updater
or promise scheduling from a skill. An agent must not stop its own host mid-task
and assume it can inspect the result. Hand off disruptive maintenance to the
host's existing operator/maintenance facility and reconcile on return.

### Optional scheduled maintenance

When the owner selects nightly maintenance, give the host one owned opportunity through a supported native
scheduler, such as the OS timer facility or a native T3 scheduled task. It is a
check that runs once per night for each target. It reads active work and current
versions, then records what actually happened:

- **No-op:** the component is already current and there is nothing to install. Do
  not reinstall it.
- **Deferred:** a change is due but unsafe now, for example because of active
  work. Record the concrete reason, the next action or revisit trigger, and who
  holds it. A deferral is never a completed update or continuation.
- **Installed, restarted, continued:** observed stages that one transaction can
  pass through in turn. Installing applies an update through the component's
  native route; restarting activates it and interrupts active turns; continuation
  means interrupted work actually resumed, read back afterwards. A restart alone
  is not continuation.

The schedule grants no authority by itself. Installing or restarting still needs
the existing delegated authority for that component and scope.

OS and packages, the desktop client, the execution service and provider CLIs are
separate transactions, each with its own channel and owner. One succeeding neither
updates nor proves another. Manual maintenance or another agreed cadence is also valid. The opportunity is not an installer and does not
guarantee unattended updates. Prove it from actual trigger evidence, not from the
configured schedule. After a migration, keep exactly one schedule per night and
target; retire the old one rather than letting two run. Do not add polling or an
approval pump.

A blocked update, reboot or client acceptance holds only that operation and the
work depending on it. Other already-authorized product and method work continues
in its existing lead and writer, with the specific hold kept visible. An agreed
short maintenance hold is different: healthy work drains or reaches a checkpoint,
every actual producer is accounted for and paused (schedules, clients, PR watches
and other wakes), and each one's prior enabled state is restored afterwards. Do
not interrupt a healthy job to start maintenance.

Keep the current official runtime and native harnesses; do not run a maintained
fork or activate a parked custom patch on the execution host. A quoted
configuration, installed file, native preference, open listener or successful
reconnect does not by itself prove the allowed tools, isolation, recovery or
resumed work.

For Omarchy, use the installed version's supported updater; inspect its prompts
and restart behavior before unattended use. Encrypted boot may still require a
person to unlock the disk. A system snapshot need not cover the separate home
volume containing T3 history and provider profiles. Verify the actual coverage;
keep private native state recoverable under the owner's retention choice. Never
grant worker sudo, bypass package failures or weaken encryption to make updates
appear automatic.

After an update, check the service, connection route, selected CLI/authentication,
loaded skills and one harmless native turn. Repeat relevant permission and recovery
checks when those paths changed. Keep prior proof at its tested version. A saved
SSH fallback may reconnect successfully without automatically returning to Connect.
Reconcile the affected persistent choices and scoped exceptions with actual native
state after relevant setup/provider changes, incidents or task needs; preserve
unrelated evidence instead of scanning the entire installation on every run.

Sources: [T3 updating](https://github.com/pingdotgg/t3code/blob/ec80933ac8cd02fec5c97b342462ccc9567cdb1e/docs/user/updating.md),
[Claude installation and updates](https://code.claude.com/docs/en/setup),
[Codex installation](https://developers.openai.com/codex/cli/),
[Omarchy update process](https://github.com/omacom/omarchy/blob/c668141e9c42b13c80c9ca4ea108e11708c5e8a5/bin/omarchy-update).

## Removal and recovery

Stop new admissions and reconcile active work first. Keep native history and the
installed source manifest. Remove only the skill folders owned by this adoption;
restore a prior reviewed copy if required. Stop/uninstall the T3 service through
its native command only when it is the intended service. Preserve other projects,
provider accounts and private state. Update the installation record from readback.

To remove an obsolete T3 project in Nightly 2873: open **Settings**, change
**Applying settings for** from **All projects** to that project, then open the
**Project** section that appears in the settings menu. Under **Danger**, choose
**Remove project**. Confirm the exact project and chat count. This removes its
threads, including archived chats, from T3; the folder and Git repository remain
on disk. Archiving a thread does not remove its project. Reconcile active work
first and obtain the owner's explicit deletion decision. Use the native action,
not manual database edits. Backup retention/deletion is a separate scoped choice.

### Same-host recovery copy

Before a disruptive change, take a consistent private recovery copy on the same
host:

1. Before stopping anything, establish an operator route independent of the
   service, so it survives the service disconnecting. Account for the relevant
   holders of the state, including connected clients and any client SSH
   auto-launch that could start another server.
2. Let healthy work drain or reach a checkpoint, then quiesce through supported
   native controls. If a relevant holder is unknown or cannot be seen, or work
   does not drain cleanly, defer before stopping. Do not stop or kill every
   process to force quiescence.
3. Check that the source is stable before the copy, take the copy, check the
   source again afterwards, and confirm the copy matches it.
4. Copy the complete required state: databases with their SQLite companion files,
   shared attachments, service configuration and the prior version.

Keep the copy private on the same host and verify a restore there. Afterwards,
check actual reconnection and provider continuation, and that held queues and
pending decisions survived. Restore exactly the prior connections and enabled
producers. A root filesystem snapshot alone does not prove a consistent home or
application recovery; its coverage and consistency depend on the actual subvolume
and data scope. Watch disk space, clock correctness and log retention. Preserve
actual failures and history, and read back the current state before any retry.
Keep commands, process identities, paths and other host facts in the private record.
