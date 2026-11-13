# Establish useful project context

Revision: 0.2.0 · Updated: 2026-11-13

Use during setup or a scoped readiness assessment. Start with the actual repo,
accepted work and existing documentation. The outcome is enough reliable context
and working controls for that work, not a required collection of Markdown files.
Assessment stays read-only; accepted setup includes ordinary in-scope repairs.

## Choose what this work needs

Set the level from the product's purpose, users, maturity, data, exposure and
consequences of failure, together with the accepted task. A prototype, internal
tool and customer-facing service may need different evidence; those labels alone
do not determine risk. The current task does not require perfecting the whole repo.

For a concrete gap, distinguish what is necessary before this work or delivery,
what can be deferred with its risk, responsible owner and revisit trigger, and
what is irrelevant. Preserve applicable obligations and existing acceptance
criteria. Deferral needs authority for the risk; it is not evidence of readiness.

Before adding a document or control, weigh its expected benefit against the cost
of establishing and maintaining it. Reuse adequate coverage. Check whether agents
can find and use the relevant context and whether controls work on representative
tasks. Evaluate quality, security, rework and human effort, not document counts or
checklist completion. Keep unrelated improvements outside the current scope.

Leave a short result in the existing adoption record, issue or task: capability,
owning source, **verified**, **required gap**, or **conditional/not needed**,
with dated evidence or a next action and responsible role. Explain why a control
is conditional or unnecessary for this task; do not require a new document to
hold this result. the project agent uses it to start ready work and route necessary setup
repairs. During accepted work, a relevant change reopens that capability's proof, not every
previously completed setup step.

## Find the source before writing

Identify where the relevant answers live. A short route in the existing README
or agent instructions is enough when the sources are otherwise hard to find.
Preserve useful filenames and conventions. One document can cover several
responsibilities; an obvious existing route needs no duplicate index.

| Responsibility | Find or establish | When to go further |
| --- | --- | --- |
| Purpose and authority | Product goals, non-goals, owner decisions and delivery boundary in the existing brief/issues/instructions | New scope, accepted risk or authority changes |
| Architecture and contracts | Components, important data flows, public interfaces and trust boundaries, linked to code/configuration | Multiple services, external integration or a changed boundary |
| Build and verification | Reproducible setup, executable checks, real tests and CI configuration; service-side rules read back | Critical behavior needs negative, integration, accessibility or performance checks |
| Dependencies | Manifests/lockfiles and the external capabilities described below | New upstream, permission, API/version contract or failure mode |
| Security and access | Relevant threats, data sensitivity, allowed actions, secret-store locations and private reporting route | Untrusted inputs, new identities/data destinations or a material risk change |
| Data and recovery | Actual schema/migrations, retention, recovery procedure and observed restore evidence | Persistent data or state that cannot simply be rebuilt |
| Delivery and operation | Chosen environment, artifact, deploy/rollback route, health checks, signals and response owner | Software is distributed or operated for users |
| Product quality | Existing UX/design, accessibility, compatibility and applicable privacy/other constraints | The product or its users/data make these relevant |

Use code, tests, manifests, workflows and service settings as their own sources.
Explain non-obvious decisions, interfaces and operating procedures in prose. Do
not transcribe configuration, package trees, issue lists or generated inventories
into a second source of truth. Point to private operational evidence without
publishing credentials, sensitive endpoints, customer data or raw findings.
The [engineering foundation](engineering.md) describes working setup, tests,
standards, design continuity, documents and agent instructions; read
[CI and delivery](ci-delivery.md) for check cadence, artifacts and environments.

For each relevant gap, state the affected capability and the next useful check
or repair. A configured control, a successful test and a documented intention are
different evidence. A missing file is not itself a defect, and a present file does
not prove secure behavior. Read only the context needed for the current task;
avoid loading every reference into every worker. Resolve contradictory instructions
at their source rather than adding another layer of instructions.

Before claiming readiness, reconcile the actual instructions, README/check commands
and local skill routes with the relevant dependency and distribution sources,
CI/protections, chosen security/reporting controls, native capability limits and
the existing setup record. Weigh each source against code, configuration, remote
readback and dated observations rather than against another document. A conflict
or unverified prerequisite stays visible as a gap; it does not become verified or
justified not-needed because one source claims it.

When work produces knowledge worth keeping, put it in the most specific existing home:

| Knowledge | Home |
| --- | --- |
| Result and proof of one task | Its existing issue/PR, with sensitive evidence in the approved private location |
| Durable application facts, architecture, dependencies or runbooks | The application's existing README, docs or source, linked from its instructions when discovery needs it |
| A standing instruction for the whole project | A short addition to the existing AGENTS/CLAUDE or equivalent convention |
| A repeatable, non-obvious procedure with concrete future use | An amended existing skill first; a focused project skill only for a real gap |
| Transferable Agentic System method | Its owning shared authoring source (Notion in our reference recipe), deliberately exported to a reviewed portable distribution |

Keep an existing wiki that works. A wiki-style docs section is optional and
needs a retrieval or maintenance benefit; do not reorganize content to fill one.
Keep one canonical explanation and link to it instead of duplicating it in docs
and skills. Do not put an application's facts into Agentic System' shared references.

## External dependencies

Package manifests/lockfiles own package versions; generated inventories can cover
direct and transitive components when needed. Use a README/architecture section
for the important dependencies that these sources do not explain. A separate
`dependencies.md` is useful only when it improves discovery or independent upkeep.
Do not require the filename or manually duplicate a dependency graph.

For an external service, plugin, runtime or other consequential dependency, record
the consuming feature and whether it requires that dependency; its upstream owner
and purpose; where configuration and the version/API contract live; allowed data
and access; and how availability, failure/recovery and updates are handled. Link
the authoritative sources. Record the responsible maintainer/role and relevant
update or vulnerability-response route. Check maintained origin, compatibility,
license/usage constraints and important transitive risks when selecting or changing
a dependency. Choose existing package/security tooling proportionately.

For example, a context plugin may use a separately maintained document connector:

| Question | Useful answer |
| --- | --- |
| What depends on it? | Reading the selected remote document; unrelated local features can work without it |
| Where is it managed? | The client's official connector and provider authorization; link their setup/configuration rather than bundle another server |
| What access exists? | Account authorization, access to the selected document, and callable read/write tools are checked separately in the actual session |
| Does the UI have that access? | Verify the panel and agent paths separately; shared branding does not imply shared tools |
| What proves readiness? | A permitted read of the intended document. Writes need their own authorized check; a read does not prove them |
| What if it fails? | Show the specific missing access or unavailable dependency and hold that feature. An empty result alone is not proof of successful context loading; do not silently copy data elsewhere |

Installation, authentication, resource access and a successful operation are
distinct observations. An optional dependency can still be required for a selected
feature. Do not expand permissions merely to make a readiness indicator green.

Distinguish what the product needs to run, what contributors need to author and
verify it, and each installation or distribution route. A project may use itself
for documented bootstrapping or dogfooding; assess that route on its real
requirements. An instruction that makes installing the product a mandatory
authoring step without a current, documented reason is a contradiction at its
source. Hold the dependent work as a required gap and route it to the
instruction's owner; do not install the product to satisfy it or silently bypass
it. Qualify distribution claims to the route they describe: a package's payload
exclusions, for example, say nothing about installing the whole repository.

## Operation and observability

Keep the agent execution host separate from the application's runtime, accounts,
data and operational signals, even when both use the same physical machine.
Record the chosen hosting model and constraints; preserve an accepted platform.
Compare alternatives only for an unresolved choice that matters to the task.

For operated software, establish how an operator detects and investigates a
meaningful failure: where deployment/health state and useful logs are found,
which metrics or traces help, how a request/job is correlated across boundaries,
and who responds through which runbook or recovery route. Use the platform's
existing facilities first. Choose alerts for actionable user/operational impact,
with a recipient and a safe way to verify the signal and response path.

Treat telemetry as data access: define appropriate collection/redaction, access,
retention and cost/volume limits. Avoid credentials, raw customer content and
needless personal data in logs; bound an agent's access to production telemetry.
Sanitize untrusted event fields and check redaction at the emitted-log boundary.
Qualify the selected signal with an authorized representative failure; installing
a collector or writing a runbook proves neither detection nor response.
Use the [OWASP logging guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
for safe event collection and [Google SRE's monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/)
for selecting actionable signals; adapt them to the actual service.

A static site may need build/deploy errors and a health check. A connector needs
diagnosable authorization, resource-access and upstream failures. A service with
customer data may also need service objectives, actionable alerts, migrations and
tested restore. Metrics, traces, a monitoring platform, `observability.md` and a
formal incident process each need a concrete purpose; no full stack is the default.

## Keep claims current

Use a small verification note near a claim about changing external/runtime state:
`Verified: <claim>; <revision/version/environment>; <date>; <check or evidence>.`
Use a compact version table when an independently versioned combination matters.
Use the project's revision convention for edited documents and skills. In this
Agentic System package, source revision/date appears at the top; Git and PRs hold the
change history. Do not impose a new metadata system on an adopting application
that already has a useful convention. A new date alone is not verification: preserve the last
observed baseline and mark a changed, untested claim as unverified. Narrow a note
to what was actually checked; source inspection is not a restore or deployment test.
An imported observation keeps its original date and source; missing dates stay
unknown rather than becoming today's date.
Drafts state untested outcomes as pending, including examples with blank date fields.

On reassessment, reuse the existing record, settings readback and dated proof;
recheck only capabilities whose code, configuration, access or versions changed.
Compare current-state claims in entry documents, such as a README's release or
pending-cutover status, with the latest delivery readback. Correct a stale current
claim within scope or route it to the project's actual owner, preserving dated
historical entries. This needs no watcher or new log.

Foundation establishes the relevant sources and initial checks. During accepted
work, the same working agent identifies and updates affected context with the
change; the project's selected review checks it against the candidate and evidence.
Authorized delivery reads back the actual result before updating operational
claims. the project agent follows up when a task, dependency update or incident reveals
concrete drift. Repair within the mandate or record the specific gap and trigger;
do not invent periodic sweeps, a new scheduler or a separate approval for each file.

These choices apply the risk-based approach of [NIST SSDF](https://csrc.nist.gov/projects/ssdf),
relevant [OWASP ASVS](https://owasp.org/projects/asvs) verification requirements and
[OpenSSF guidance](https://best.openssf.org/Concise-Guide-for-Developing-More-Secure-Software).
Select applicable controls and prove them; these references confer no certification
or guarantee of security. [SLSA](https://slsa.dev/spec/v1.2/build-track-basics)
helps distinguish artifact provenance from stronger build-integrity controls.
