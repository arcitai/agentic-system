---
name: agentic-brief
description: Use when the owner or their planning agent asks where things stand, wants to catch up after a break, or needs to make a decision; or when a project lead resumes after a restart, compaction or owner return. Produces a read-only briefing, one consolidated decision handoff and a continuity check from native records.
license: MIT
metadata:
  version: "0.1.34"
  updated: "2026-11-06"
---

# Agentic Systems Brief

# Briefing, decisions and continuity

Use this method to let a person pick up the work in one read, decide what is
genuinely theirs, and let the responsible lead continue without relying on any
single chat staying awake. A project's AgentOps uses it for its own project. An
owner's optional planning agent may use it to request, combine or relay leads'
briefings and to prepare recommendations; it acts only within an actual owner
delegation and does not silently take over a project's lead, follow-up or mandate.
The installation chooses who uses it.

Read communication preferences in [references/preferences.md](references/preferences.md) when the person has
stated any, or before contacting them outside the current conversation.

## Briefing

A briefing is read-only. Producing it never dispatches, steers, merges, answers a
decision, cleans up, retries or changes task state. Build it from the current native
records: the project's task record or ledger, its issues/PRs, native thread and job
state, schedules and recorded holds. Do not rely on memory of the chat. If a source
is unreadable, say which one and what the briefing therefore cannot show.

Lead with what needs the reader, in plain words:

1. **Waiting on you:** each genuine owner decision, linked to its handoff.
2. **Blocked:** what is stuck, who actually holds the next action, and since when.
3. **In progress:** active work with its real state, such as queued, started,
   in review or held. A sent message is not started work.
4. **Done since the last recorded briefing,** or since a time the reader names:
   delivered outcomes with links, labelled as
   decided, implemented, reviewed, merged, published or installed. These are
   separate states.
5. **Next follow-up:** who owns it and the real native trigger, or the named
   missing capability (see Continuity).

Keep it short enough to read on a phone. Put identifiers, logs and evidence behind
links. Keep an adverse result or missing check visible when it affects a decision.
An operational summary is not a backup. It does not preserve history or prove
that anything can be restored.

## Decision handoff

Bring a decision to the owner only when it is genuinely theirs:

- admitting work or accepting delivery, unless the owner delegated it for this scope;
- a destructive, irreversible or security-sensitive step outside an explicit delegation;
- a choice the mandate leaves open, or one that new evidence has materially changed.

Decide unambiguous calls inside the accepted scope yourself and record them. A reviewer's suggestion or a worker's
question does not by itself amend the accepted scope.

Write one consolidated handoff per decision gate, not one per question:

- **Decision needed:** one sentence, and why it is the owner's.
- **Candidate:** the exact artifact, version or hash and its current evidence.
- **Options:** realistic choices with their consequence, including "hold".
- **Recommendation:** yours, with the reason.
- **Held meanwhile:** what waits on the answer, and what independent work continues.
- **Who follows up:** the holder and the real trigger.

Record the handoff in the project's existing record or issue, then present it.
Silence is not approval. A pending decision holds only the affected step. When the
candidate or its basis changes, check again whether an earlier answer still applies.
Record the owner's answer where the work's record lives before acting on it.

## Continuity

After a restart, compaction or new session, or when the owner returns, rebuild before
acting. Reread this skill, the owner's current request, the retained task record,
recorded decisions and holds, and each recipient's native state. Reconcile what
actually happened since the last recorded step, including uncertain writes, before
any retry. Then brief.

Follow-up remains the lead's responsibility until the work actually moves. State
how the next follow-up will happen:

- a native trigger that is actually selected and verified, such as a bound native
  schedule, an issue or PR event route, or the next owner message to the same lead;
  or
- the missing capability, named as such, with the holder able to provide it.

A skill cannot wake an agent. Do not promise a reminder, message or wake-up that no
selected and tested native route will deliver.
