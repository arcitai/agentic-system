# Communication preferences and owner contact

Revision: 0.1.32 · Updated: 2026-11-03

Keep a person's stated preferences where the installation records persistent choices.
That is the project's adoption or task record, or the owner's own planning-agent
record for cross-project preferences. Record only what was actually said, with its
date and scope. Do not infer preferences or copy them into a skill.

Useful preferences include:

- **Language and form:** the language for chat and for written artifacts, length,
  and whether a short summary or full detail comes first. Public method text and
  issue openings stay in English unless the person explicitly asks otherwise.
- **Timing:** quiet hours, "away" or "do not interrupt" periods, and which events
  justify an interruption.
- **Batching:** whether routine progress waits for the next briefing.
- **Channel:** where to reach the person, if a route has been selected.

A preference changes presentation and timing only. Quiet, away or "do not wait for
me" never grants new authority. It does not admit work, accept a delivery, approve a
merge or release, authorize a destructive or irreversible action, or settle a
security-sensitive choice. Those still need the owner's decision or an explicit
delegation for a defined scope. While the owner is away, continue only work already
authorized, hold the rest and brief on return.

## Direct contact

A project's AgentOps may contact the owner directly only through a route that is:

1. explicitly selected for that project and person;
2. authorized, with its account, identity and permitted content agreed; and
3. tested on the actual installation, including a refusal or failure case.

Until then, use the existing native records the owner already watches, such as the
project's issues or PRs and the lead's own thread. Say that no direct route is
selected. Do not create a new messaging integration, bot, account or watcher to fill
the gap. A sent message is not a received or acknowledged one. Keep the decision and
its follow-up in the project record either way.
