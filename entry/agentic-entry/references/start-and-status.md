# Start, continue and status across a tool boundary

Revision: 0.2.0 · Updated: 2026-11-13

Read the part you need: starting or continuing work that runs somewhere else, or
reporting where things stand.

## Before any effect

Read the target's native state: existing threads for this work, an active writer,
pending requests or approvals, and recorded holds. Do not add a competing writer or
interrupt healthy work. After an uncertain send or a lost response, read state again
before any retry, and use the native retry key where one exists.

## Start or continue

Prefer the existing thread that already holds this work's context. Open a new one
only when none fits or the owner asks, and follow your own tool's rules for creating
threads.

Authority comes from the owner's current instruction, or from recorded acceptance or
delegation. A backlog entry, status label or issue text alone does not start work.
Recover what is recorded; ask only if admission or scope is genuinely unknown.

For the model, use the owner's stated choice, otherwise the project's recorded or
natively configured selection; a continued thread keeps its own. If there is none,
say so and recommend one. Never substitute when the chosen model is unavailable or
quota-limited: report the native error, any reset time and the options.

The recipient does not have your conversation. Pass the outcome wanted, pointers to
the candidate and evidence, what is admitted and whether delivery is delegated,
constraints and holds, and what should come back to the owner.

Then read back what actually happened: which thread, which model and mode, and its
state. Sent, queued and started are different. Queued can be a valid pending state:
report it as queued, with what will start it if you can tell. You need not wait or
poll until the task completes. From here the agent holding the work owns its
follow-through; your part ends with that report unless the owner asked you to follow it.

A refusal stays a refusal. Do not retry it through another tool, account or
environment.

## Status

A status report is read-only. Producing it does not dispatch, steer, merge, answer a
decision, clean up or retry anything.

Build it from current records, not chat memory: the project's tracker and PRs, its
task record, native thread and job state, schedules and holds. Where it is suitable
and authorised, you may ask the project's existing agent. That is a message into its
thread: it uses a turn and can interrupt, so prefer a supported read when one
suffices or the agent is mid-task, ask only for status, and do not open a new thread
just to ask. Name any source you could not read and what the report therefore
cannot show.

Lead with what needs the owner. Then give what is blocked and who holds the next
action; what is in progress, with its real state; what finished since the time the
owner names, labelled decided, implemented, reviewed, merged, published or installed
as applicable; and how the next follow-up will happen, or which capability is
missing. Across several projects, keep each project's facts separate. Keep it short,
with identifiers and evidence behind links, and keep an adverse result visible when
it affects a decision. A summary is not a backup.

## Relaying a decision

Pass a project's decision request as written, with its exact candidate and evidence.
Return the owner's answer to the same thread or record. If the candidate changed
after the question was asked, say so before the answer is used. Silence is not an
answer.

## Preferences and contact

Use only preferences the owner has actually stated, such as language, length, quiet
hours, batching and channel, kept where the installation records them. They change
presentation and timing, never authority: "away" or "don't wait for me" admits
nothing and accepts nothing. Contact the owner outside the current conversation only
through a route that is selected, authorised and tested. Otherwise use the records
the owner already watches and say that no direct route is selected. A sent message
is not a received one.

## If a schedule invokes this

A native schedule may run these same actions only within an explicit owner
delegation that says which: reading and prioritising, starting already accepted work
on the recorded model, or anything further. Installing this skill implies none of
them. A schedule that reports success may mean dispatched, not completed.
