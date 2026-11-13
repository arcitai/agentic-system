---
name: agentic-entry
description: Use when an assistant working outside a project is asked what Agentic System is, which project, context home or method revision a request belongs to, or to start, continue or check work in an Agentic System project it is not already working in. Not needed for a task given directly inside a project.
license: MIT
metadata:
  version: "0.2.0"
  updated: "2026-11-13"
---

# Agentic System Entry

Load this when you are an assistant outside a project and the owner asks about Agentic System, or asks you to find, start, continue or check work in one of its projects. It is a capability you use, not a role: it does not make you a project's manager, and no work has to pass through you. The owner can always address a project's agent directly. If you are already working in the project on a task given to you there, follow that project's instructions; this skill adds nothing.

## What Agentic System is

Agentic System is the prepared ground a project's agent works on, plus the boundaries around it: an agent environment (tools, model, skills, access), a project foundation (goal, context, standards, checks), and operations and maintenance. On that ground one project agent carries an accepted task from research to a checked result on the model the owner selected, and calls a fresh reviewer, a pair or parallel helpers when that helps. There is no required manager, chain of stage agents or upfront split into tickets. Each project selects its own methods, checks and domain knowledge, called its work module. Native tools and service permissions enforce access; documents and skills do not. For more, point to the installation's own guide or context home instead of restating it.

## Find the real project and version

Resolve identity from records and native state, not from memory: the project, its workspace or environment, any existing thread that holds the work, its context home, and the method revision it selected. A familiar thread title is not identity. A released distribution, the authoring edition and an installed copy can differ; say which you read. If a record is unreadable from where you run, name it and what you therefore cannot tell. Do not widen access to find out.

Read only what the request needs. Explaining the method needs no project records. A question about one project needs that project's records, not an inventory of all of them.

## Match the request

- **Understand the method:** answer from the section above and the guide. Load nothing else.
- **Set up, adapt, assess or maintain a project or host:** use `agentic-foundation` if it is available by name. Otherwise read it explicitly from a reviewed distribution, or say it is not available here. Explicit reading is not native discovery.
- **Do work in a project:** if the request is to you and your current workspace and access are the right place for it, do it under that project's instructions. If the work belongs in the project's own environment, or an existing thread there already holds its context, start or continue it there with [references/start-and-status.md](references/start-and-status.md).
- **Where things stand, in one project or several:** the status part of the same reference.
- **Compare models, methods or settings:** use `agentic-evaluate` if available. Otherwise say so and help frame the decision and the evidence that would settle it.

## Limits that travel with you

The owner's current clear instruction can admit work and delegate its delivery. Recover context and recorded decisions first, and ask only for a decision that is genuinely missing. Do not add an acceptance step the owner did not ask for.

The owner chooses the model. You may recommend one with reasons. Do not select or switch a model, account or paid tier unless a recorded delegation covers that choice. If the chosen model is unavailable, stop and report.

This skill grants no access. Your own environment's reach is not the project's boundary: use it for project work only as the owner has authorised, and keep personal connectors and credentials out of the project's execution environment.

Keep no private queue of project work and do not become a standing relay between projects. State lives in each project's own records.

Requested, installed, discovered in this session and actually used are four separate claims about this skill.
