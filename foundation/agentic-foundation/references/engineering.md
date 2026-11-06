# Engineering foundation for a software project

Revision: 0.1.21 · Updated: 2026-10-23

Use when preparing or assessing a project's engineering conditions: setup, checks,
standards, design continuity, documentation, delivery and operation. [Project
context](context.md) decides which capabilities the accepted work needs and how to
record the result; this guide describes working foundations and their proof. Read
[CI and delivery](ci-delivery.md) only when branch policy, checks, automation,
artifacts or environments change. A small library, a document repository and an
operated service need different evidence. Select applicable obligations; this is
not a checklist to complete.

## Start from the actual project

Inspect the repository, instructions, history, remotes, licenses, local work and
accepted decisions first. Repair a legacy or forked project in place: never run a
template conversion, reinitialize or reseed Git history, replace remotes or discard
local edits. Before enabling inherited automation, check contradictory commands,
inherited contacts, upstream workflows, licensing and provenance. Preserve working
equivalents, unique history and a healthy documentation tree. Interrupted setup
resumes from current state and evidence, with one setup writer. A read-only
assessment uses the same criteria without editing, provisioning or starting jobs.

Resolve material gaps in audience, status, data sensitivity, operating owner,
budget and target environment from available evidence before asking. Keep the
application's runtime, accounts and data distinct from the agent execution host
and its build compute; a preview service and an isolated worker can need different
resources. Do not choose Kubernetes, a cloud provider, a VPS or a long-lived dev
branch by default. A new project's name or starter template does not determine its
architecture, design, operating contact or deployment topology. An explicit
unresolved decision is useful seed state; it does not pass acceptance.

## What working foundations prove

| Capability | Establish from the project | Useful proof |
| --- | --- | --- |
| Repository and intake | Canonical GitHub repository, preserved origin/history, issue-to-task route, branch/PR policy, permissions and protections | Remote identity, settings and permitted actors read back; one issue traced to its intended check and review target |
| Reproducible setup | Actual toolchain and native libraries, ecosystem manifests and lockfiles, frozen install, start/check entrypoints, fixture services and platform constraints | A clean checkout on the selected host installs the locked versions and runs, without hidden laptop state |
| Standards and design | Project-specific conventions, enforced checks, material exceptions and maintained examples; accepted visual/interaction direction or API/CLI contracts | Changed behavior inspected against those sources; stale guidance updated in the same change |
| Testing and acceptance | Behavioral unit/integration/end-to-end coverage proportionate to risk, canonical commands, controlled fixtures, negative and recovery cases, known limits | The relevant checks run, and a meaningful defect makes them fail. An empty, filtered-out or accidentally skipped suite is not proof |
| Security and data | Exposure, authorization/trust invariants, supply-chain controls, secret references, synthetic fixtures, migration/retention/reset needs | Affected denial, initialization and recovery paths exercised; sensitive data stays out of source and artifacts |
| CI and delivery | Required PR evidence, full-check cadence, immutable source/artifact/version identity, environment separation | See [CI and delivery](ci-delivery.md) |
| Operation and recovery | Health/logs, diagnosis, stop/restart, updates, incident intake, cleanup, last known good state and responsible operator | A failure observed with its rollback, restore or reset path; an unrehearsed procedure stays labeled unrehearsed |

Architecture, dependencies and observability follow [project context](context.md).
A SECURITY file is a reporting route, not a security review of the exposure.

## Files and configuration beyond documentation

Select concrete files for the actual stack. A manifest, Dockerfile or workflow is
useful only when it describes a supported working path.

- Commit a root `.gitignore` for credentials, local state, caches and generated
  output. Inspect already-tracked files with Git and test example paths against the
  rules so required fixtures, lockfiles and safe examples stay trackable. Ignore
  rules cannot remove a secret already in history; that needs rotation and its own
  remediation decision.
- Preserve inherited license texts and notices, and record their provenance. Record
  the product's licensing decision; template attribution does not license newly
  authored code, and a private repository does not imply an open-source license.
- Use ecosystem manifests, lockfiles, actual version pins and a frozen/locked install
  command. Configuration examples hold safe defaults and secret-store references,
  never live values. A project without environment variables needs no invented
  `.env.example`.
- Keep formatting, lint, file modes, line endings and binary handling in executable
  configuration such as `.editorconfig`, `.gitattributes` or the linter's own file.
  Agent instructions name the check route, not the mechanical rules.
- Use real workflow, deployment and provisioning definitions. For containers,
  inspect the build context and `.dockerignore`. No container or infrastructure
  framework is required by this guide.
- Reuse sufficient issue and PR templates. An issue captures outcome, scope and
  acceptance; a PR identifies source/base, actual checks, documentation impact and
  relevant recovery. Security reports keep a private route. CODEOWNERS needs real
  owners and a review policy that someone actually performs.
- Repository, Actions and environment settings, required checks, secret stores and
  permitted actors are remote state. Read them back and record plan or access limits;
  writing a file does not configure them.

## Documentation with a maintained owner

There is no universal filename checklist. Each responsibility the project actually
has needs one findable, maintained home. A new application commonly needs: an entry
README (purpose, audience, status, owner and start route); concise agent instructions;
contributor guidance with real install/start/check commands, change rules and test
limits; architecture; design or interface contracts; a security reporting route;
and infrastructure, deployment and operations guidance once the software is
operated. One guide can own several responsibilities. Preserve existing names and
capitalization and link to them instead of copying their body. A docs index helps
when the map is otherwise hard to follow. Do not pre-create a page for every
heading, impose a docs-site generator or invent historical rationale.
Non-application projects need their authoring, usage and validation sources, not a
fictional hosting or visual design setup.

GitHub surfaces contribution guidance from `.github`, the root or `docs`, with
`.github` taking precedence; reconcile competing copies and check the surfaced one.
README and SECURITY have their own discovery. Architecture, design and testing
filenames are project conventions. License detection is not a licensing decision,
and agent instruction discovery is a separate harness concern.

For each behavior, interface, configuration or infrastructure change, update the
canonical document in the same reviewed change or state why it is unaffected. Name
who keeps it current. Verify commands, links, contacts and examples against actual
code, workflows and resources; a date refresh is not maintenance. Generated reference
has a canonical source and a reproducible command. Mark superseded decisions and keep
useful history at its owner. Keep secrets, restricted incident records and raw
private logs in their authorized stores.

A short feature map in an existing index can link user outcomes to intended
behavior, implementation and checks when behavior is hard to locate; keep it current
in the same change and do not inventory every symbol. For recurring agent mistakes,
improve executable checks first, judgment-dependent standards second and routes to
existing information third. Remove stale or duplicate guidance.

## Code standards

Read existing standards and executable configuration before writing. A concise
contributor section is enough unless conventions need their own home; preserve an
existing standards file. Record accepted decisions with rationale, examples from
current source and material exceptions. Tools own mechanical rules. Do not endorse
every observed legacy pattern or fill a file with generic advice. Review task
correctness and standard conformance separately, and report missing guidance as
unknown rather than inventing a rule.

## Design and interface continuity

Keep accepted direction separate from observed current behavior. Record what was
decided and where, what the product actually does now, and which differences are
intended changes not yet built. Preserve an existing identity unless a change to it
is accepted.

- Keep canonical tokens and components in one source, normally code or token files,
  and link to them. Never maintain competing copies of a token.
- For affected flows, cover hierarchy, responsive layout, accessibility, loading,
  empty and error states, and relevant interaction feedback.
- Point to real code, routes, stories or screens as examples, not mockups that have
  drifted from source.
- A separate design-system document is warranted when a reusable component library
  or theme needs its own maintained scope. It then owns reusable primitives and the
  design document owns project flows and composition.
- API/CLI-only products use interface contracts and state why visual design does
  not apply.
- Update affected design or interface documentation with the code change. Verify
  the actual rendered result and interaction in a browser or the real client at the
  relevant sizes, including a failure, empty or loading state. A passing unit test
  or a capture of another build does not prove the change.

No particular design tool, design skill or runtime is required.

## Agent instructions and harness adapters

Keep agent instructions as a compact execution contract: non-obvious setup and check
prerequisites, accepted architecture/security constraints, generated-versus-source
boundaries, actual delivery authority, recurring evidenced pitfalls with rationale,
and short "read this when changing X" routes. A discoverable fact can still merit
a line when misreading it causes a concrete error. Leave file trees, dependency
inventories, duplicated examples, tutorials, runbooks and specialist procedures to
their owning sources. Curate contradictions instead of appending rules; a one-off
failure is not automatically policy. Nested instruction files need real scope
differences. Do not preload every document or impose a line or token quota.

Keep one maintained instruction body per scope. Harnesses differ in which files
they discover and whether they read instructions in parent directories. When the
selected harness does not read the canonical file, add the smallest adapter it
supports, such as its own instruction file containing a documented import or a
short pointer to the canonical body, rather than a second copy. Check the mechanism
against the harness version in use. Verify discovery and route-following in a
representative actual invocation from the intended working directory; a file or
link check does not establish agent behavior.

## Exercise and hand back

Exercise clean setup, the real checks and relevant failure/recovery paths with
controlled data. When non-production delivery is in scope, verify the tested
artifact running in its actual environment as described in
[CI and delivery](ci-delivery.md). A document-only project needs its applicable
authoring, validation and delivery checks instead.

Check that a representative agent finds the right instructions and checks. Return
usable entrypoints, source/environment and version-bound evidence, changes made and
remaining gaps. Distinguish a prepared repository, an exercised non-production
delivery path and a production-qualified application. A specification, template,
generator run or green unrelated demo is an intermediate result. Readiness grants
no implementation, merge, release or production authority; those follow the owner's
decisions and explicit delegation.

## Provenance

This guide and [CI and delivery](ci-delivery.md) adapt and generalize the
`aios-project-foundation` 1.1.1 skill from
[AIOS-plugin](https://github.com/onlinesourdough/AIOS-plugin) at commit
`3977b4de6da004bdbca47e383862390c2e4cd1fe`, MIT License, Copyright (c) 2026 Gustav
Anderson. The same license text accompanies this skill. Agentic Systems requires no
installation of that plugin, now The Onlinesourdough Method (OSM).
