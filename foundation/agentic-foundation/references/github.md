# Prepare repository work tracking and delivery

Revision: 0.2.0 · Updated: 2026-11-13

Inspect the actual repository, owner, default branch, existing instructions,
checks, labels, Projects and deployment rules. Preserve established conventions.
Use GitHub's native CLI/API/UI; Agentic System has no label cache or workflow database.
Check the authorized account and exact destination before changing them.

## Qualify the connection

GitHub authentication belongs to the OS account running the execution service.
Check `gh auth status` there, then read the intended repository, a relevant issue
or PR and its checks. Git fetch/push credentials and Project permissions are
separate capabilities; test the read paths and qualify writes only as part of an
authorized action. A browser login or successful Git clone does not establish all
of them. Reuse existing credentials only when their actual grants fit the agreed
boundary; request only missing access.
Never print tokens or copy a personal credential store into the execution account.

For a new scoped connection, record the repositories, required operations,
credential's OS account and storage, authorizer, expiry, and revocation route.
A role name is not a credential boundary. For a small single-owner setup, a
fine-grained personal access token can limit writes and private reads to selected
repositories and permissions. Give no administration, secrets, workflow-write,
status/check-write or organization permissions unless the accepted task needs them. All public
repositories remain readable; a successful public read does not prove scoping.

Use a maintained native GitHub App integration when its installation permissions
and supported endpoints fit better. Do not build an App backend or token service
just to satisfy this recipe. If no native route provides a required capability,
record the limitation rather than falling back to a broad personal login.

Keep the project agent's coordination/delivery credential outside worker environments.
Workers need their selected files and tools; remote write access is conditional.
An inherited token, credential store/helper, SSH key or forwarding socket that
exceeds the worker's boundary holds dependent execution until it is excluded or
the owner explicitly resolves that access.
Check actual allowed repository/issue/check operations and a refused operation
against a known existing private repository outside the grant. Test writes only
through authorized disposable resources or real accepted work. For a permission
that must be absent, verify an applicable refusal without changing real settings.
Check the actual rules protecting delivery, including bypass actors and the
required checks' source: token scope does not require PR review or stop a direct
push by itself. An inaccessible
protection setting stays unverified, and is not a reason to grant administration.

Qualify the required write path through a real authorized PR or task update.
Use a disposable credential/resource for destructive revocation tests; otherwise
verify the native removal route and record revocation as untested. Expiry alone
is not a revocation test. Keep credential values in native secret storage; keep
private targets and grant details in private installation records.

Before the first commit, check `git var GIT_AUTHOR_IDENT` and
`git var GIT_COMMITTER_IDENT` in the intended checkout. GitHub login does not
configure commit attribution. If missing or wrong, use the approved identity at
the selected repository or execution-account scope; preserve existing overrides.
Use the account's [GitHub-provided noreply address](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
when privacy is needed. Never invent an author. Read back the identity on the
first authorized commit; no extra test commit or credential change is required.

For T3 0.0.45, use **Settings → Source Control → Rescan** after authenticating on
the server, then confirm its account/status in that environment. This is native
GitHub integration; there is no separate Agentic System login. See
[T3 source control](https://github.com/pingdotgg/t3code/blob/v0.0.45/docs/user/source-control.md).

## One work-status source

Choose the existing GitHub Project's **Status** field as the reference workflow.
For a new project, a useful starting set is Not planned, Triaging, Ready,
In progress, Review and Done. These are defaults to adapt, not hardcoded runtime
states. The source is the Project field and its actual option IDs. Put Not planned
before Triaging; keep it open for parked ideas with a revisit trigger.

Record the human admission decision or its explicit delegation before moving
implementation work to Ready. Use Triaging for active assessment and research;
untouched or deliberately parked ideas can remain Not planned with a revisit trigger.
Track a concrete dependency or owner decision in the issue; do not turn all parked
ideas into blocked tasks. Read the accepted priority before picking backlog work.

Use labels for useful categories such as bug, feature, research, security and
scope/area. Reuse real names and colors from GitHub. Avoid a second set of labels
that mirrors Status. A GitHub edit is reflected natively without Agentic System syncing it.

Inspect first, then create only missing resources. For a new org Project:

```sh
gh project list --owner YOUR_ORG
gh project create --owner YOUR_ORG --title "Agentic System" --format json
gh project link PROJECT_NUMBER --owner YOUR_ORG --repo YOUR_ORG/YOUR_REPO
gh project field-list PROJECT_NUMBER --owner YOUR_ORG --format json
```

Replace the placeholders with inspected identifiers. Do not repeat creation after
an unknown response; list and reconcile first. In the Project UI, edit the existing
Status options, create a Board view grouped by Status, and save useful filtered
views. The GraphQL API is available for supported field/item operations. Read the
settings back; a guide or local JSON file does not configure GitHub.

Projects needs the account's applicable Project access. For a GitHub CLI OAuth
login that lacks the scope, deliberately request it with
`gh auth refresh -h github.com -s project`; listing alone can use `read:project`.
Use the appropriate permissions for other token types. For a user-owned Project,
use `--owner @me` instead of an organization name. Do not repeat login when the
current authorized account already has sufficient access.

If adopting an existing field, map its actual semantics rather than renaming
historical work without a migration. Closing as `not_planned` is declined work,
not delivered Done. Configure built-in workflows accordingly: an unconditional
closed-issue → Done rule can erase that distinction. An open backlog field and a
GitHub closure reason are different records.

## Admission and automation

An issue can come from anyone with access to the repository. Identify trusted
owner decisions independently from its body. The initial route is explicit:
give the project agent the issue or an accepted backlog with its execution mandate.

For later webhook/scheduled intake, use a qualified native T3/harness facility.
Authenticate the sender, bound repositories/actions, read current state and
reconcile duplicate delivery. A valid GitHub webhook signature authenticates the
event, not every issue author's instruction. Do not place a persistent agent on
an untrusted PR runner or build another Agentic System queue.

## Checks and delivery

Use the application's real test/build/lint checks. Keep workflow permissions
minimal, dependencies/actions reviewed and pinned, execution bounded and secrets
out of untrusted PRs. Do not carry Agentic System's method-validation workflow into an
application as a substitute for meaningful application tests.
Identify the relevant dependency-update and vulnerability-response route. Inspect
effective workflow/token permissions, and native dependency alerts and secret
scanning/push protection where available and appropriate. Distinguish configured,
observed and unavailable controls; do not enable paid services or treat a scanner
score as a security guarantee.
When the selected private security-reporting route is GitHub private vulnerability
reporting, read its remote setting back through the API or repository settings;
disabled, inaccessible or unchecked state stays a visible gap. A SECURITY file
documents a route but does not prove it is enabled. Another monitored private route,
or a justified not-needed choice for a small private repository, remains valid.

For branch policy, PR and full-check cadence, the optional three-hour batch profile,
artifacts and preview/staging delivery, read [CI and delivery](ci-delivery.md).
Configure actual branch rules/required checks and applicable deployment protections
in GitHub. Read them back, including the actors permitted to approve or bypass them.
A workflow file alone does not enable those controls.
Record plan/access limitations without changing billing or repository visibility.
One person's accounts may be unable to approve their own PR: independent model
review and GitHub-required review are distinct. Preserve configured controls;
do not bypass them to claim the autonomous path works.

Before delivery, identify the exact reviewed candidate, check results, owner or
delegated acceptance, destination and recovery. Refresh affected proof after
changes/rebase. Read back the merge/release and, when in scope, verify actual
installed behavior. Published, installed and validated are different states.
Update affected delivery documentation to match the observed revision/environment.
An untested deployment, rollback or restore remains unverified; publishing a release
does not advance those verification dates. Retain private evidence at its approved
location and link only a safe summary from public documentation.

## Contributor credit

Keep the human author and use the native Co-authored-by attribution for harnesses
that actually contributed. Preserve these trailers when squashing. Codex's native
identity is `Codex <noreply@openai.com>`; retain Claude's actual native selected
model identity when it contributed. Do not invent another harness's email or
rewrite history just to populate a graph. Review-only participation belongs in
the PR's review evidence.

This is attribution, not another GitHub login or permission boundary. GitHub
associates commit emails with accounts and applies default-branch/contributor
rules, so a visible trailer need not immediately create a separate avatar in the
contributors graph. A shared credential still has its actual shared grants.
[Multiple authors](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors),
[contributors graph](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-a-projects-contributors).

Sources: [Fine-grained tokens and limitations](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens),
[GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps),
[Projects API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects),
[built-in workflows](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations),
[rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).
