# Branches, CI cadence and delivery

Revision: 0.1.9 · Updated: 2026-10-10

Use when changing an application's branch policy, checks, automation, artifacts or
environments. Preserve a healthy accepted workflow, including existing per-PR full
checks, scheduled verification and continuous delivery. A small project whose full
checks already run on every PR needs no additional batch workflow. Agentic Systems installs
no workflow, runner, scheduler or deployment; this guide enables nothing by itself.

## Branches and revision identity

Without an accepted alternative, start with main plus short task branches.
Staging or preview can follow main; it requires neither a dev branch nor a
production release. If a dev/integration branch is selected, specify feature PR
targets, promotion checks into main, release authority and synchronization after
fixes. Record the actual default and integration branches and required checks.

Trace issue → isolated task at a recorded base SHA → reviewed candidate → PR to the
selected target → current integration checks → authorized environment delivery.
A moving branch name never substitutes for the source revision. A changed base,
conflict resolution or edited candidate needs relevant fresh checks and review.
A merge into a non-default branch does not automatically close a GitHub issue;
read back issue, PR and deployment state rather than equating those events.

## Three-hour batch profile

This is an adaptable application profile: necessary checks on every PR revision,
plus complete verification and build batches every three hours where the owner or
project selects that cadence. Adapt the interval and lanes to demonstrated needs
and existing deployment requirements. Do not install it in a project that has no
real application checks to run.

- **Every PR revision** receives the necessary checks and build prerequisites.
  Scope expensive lanes from real source and dependency relationships. Changes to
  shared code, toolchain, lockfiles, CI or unclassified paths select broader
  validation. An unavailable comparison base fails planning instead of becoming an
  empty diff. Include deleted and renamed paths in the comparison.
- **Concurrency**: cancel superseded runs for the same PR. Serialize full batches
  and actual delivery so a newer batch never interrupts a valid running deployment.
  Remove a duplicate full push trigger when PR checks plus batches already provide
  the intended evidence.
- **A full batch** verifies the recorded integration SHA and builds complete
  artifacts identified by that source. Skip expensive lanes only when a complete,
  successful scheduled or manual full run already covers that exact source SHA
  under the applicable workflow/policy version. A scoped PR pass is insufficient.
  A failed, cancelled or unverified revision remains eligible and is retried at the
  next interval. A manual run can always force a full batch.
- **An idle interval** runs one lightweight metadata check: no checkout, dependency
  install, test, build or additional acceptance runner. It still consumes some
  Actions runtime; never describe an in-workflow guard as zero cost.
- **A stable aggregate check** is the required merge barrier. It fails on planning
  or API errors and when any required lane fails, is cancelled or is skipped
  unexpectedly. GitHub can report a skipped job as successful, so a skipped check is
  not a barrier. Only a schedule whose idle decision is explicitly proven may skip
  the aggregate; PR and manual events, and any missing decision, keep failure handling.

Skip evidence identifies the tested source SHA, its branch, the workflow/policy
version and the complete result. Record the tested SHA explicitly: a scheduled
run's own commit is the default branch's head, not necessarily the source that was
tested.

## Scheduler facts

GitHub runs scheduled workflows from the default branch, and the workflow must exist
there and be enabled. Scheduled runs can be delayed, and may be dropped under high
load. Cron is interpreted in UTC unless the optional timezone is set; this profile
records its schedule explicitly in UTC and uses a staggered minute, such as
`17 */3 * * *`, rather than the top of the hour. Promise a cadence, not
punctuality. If a dev/integration branch supplies the batch source, resolve, check
out and record that branch's SHA; the scheduler's main SHA is not evidence for dev.

A configured timer means the workflow is on the default branch and enabled, read
back from GitHub. Observing a scheduled event and its result is separate evidence.
See [schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
and [concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency);
use current provider documentation when implementing the workflow.

## Qualify the cadence

Read back Actions permissions, token scopes and the required-check protection for
the actual target branch and actors. Record unsupported plan or access limits; a
workflow file does not prove enforcement. Qualify a passing case and meaningful
failing cases, as applicable: a missing comparison base fails, a failed or
unexpectedly skipped lane fails the aggregate, a failed batch is retried, a prior
full success is reused only for its exact SHA and policy version, and an idle
interval does no checkout or build. Never weaken or disable the barrier to obtain
a green result.

## Delivery evidence

Keep the project's full acceptance command distinct from narrower PR checks.
Record source and artifact revision, build/check result, target environment and
access route. Production qualification needs its own release criteria even when PR
checks pass. Keep working CD rather than disabling it because a batch cadence was
chosen. A schedule adds no deployment or production authority; delivery follows
the owner's decision or explicit delegation.

A requested preview or staging target runs the tested artifact, identified by
source and artifact identity, with the intended configuration and controlled data.
Exercise useful behavior, health and log visibility, applicable migrations, and a
failure with its rollback or reset. Document secret references, cleanup, limits and
the responsible operator. An uploaded build, a successful deploy command or an
untested runbook does not prove this path. Never deploy a revision that lacks the
project's required verification; under the batch profile, a missing, failed or
unverified full batch blocks it. Infrastructure, deployment and operations
guidance must match the resources and commands actually exercised.

Provenance: adapted from AIOS `aios-project-foundation` 1.1.1; see the
[engineering guide](engineering.md#provenance).
