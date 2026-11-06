---
name: agentic-spec
description: Turn an accepted application or defensive outcome into a bounded implementation brief with observable acceptance and relevant recovery.
license: MIT
metadata:
  version: "0.1.34"
  updated: "2026-11-06"
---

# Specify

Reuse the project's vision, architecture, standards and accepted answers. Research
factual gaps before asking the owner to repeat context. For a small accepted fix,
an issue and its acceptance check can be sufficient.

Define intended behavior, allowed changes, exclusions, dependencies, needed tools,
observable proof and delivery boundary. Separate facts, assumptions and open
decisions. Include data/access constraints and recovery where consequences justify
them. Preserve explicit admission and delivery delegation; do not add phase gates.
Identify the affected architecture, dependencies, trust/data boundaries and
operational signals, with routes to their existing sources. Include needed context
updates and verification in the same scope; a small fix needs no new docs framework.

For a material unresolved design choice, compare concrete alternatives against
the project and select the least maintenance that meets the need. A small local
experiment may settle empirical uncertainty. State what observation ends it;
do not expand a trial into a new platform or replace the accepted product.

Break substantive work into independently reviewable vertical slices. Each slice
should demonstrate useful integrated behavior with relevant failure checks.
Prerequisites belong with the outcome they enable; avoid isolated layers that
only become useful at the end. Complete the accepted outcome across those slices.

Use real issue identifiers for dependencies and the project's current tracking
fields. A plan or board status is not a scheduler or proof of active execution.
Keep unresolved future scope as questions rather than speculative tickets.

Return a usable brief, checks and remaining decisions. Substantive implementation
requires accepted admission or its explicit delegation. If the mandate already
covers it, continue without asking for another approval of the same scope.
