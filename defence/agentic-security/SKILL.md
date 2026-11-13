---
name: agentic-security
description: Investigate an authorized security or defensive question and distinguish candidate findings, validation, remediation and recovery evidence.
license: MIT
metadata:
  version: "0.2.0"
  updated: "2026-11-13"
---

# Security and Defence

Identify the authorized target, revision/environment, question, allowed actions,
data boundary and evidence destination. Application development does not authorize
testing unrelated hosts or production. A missing boundary holds the affected
probe; continue permitted source analysis where useful.
Use the project's current threat, dependency and operational context. When the
question changes a trust boundary, connector or data class, identify the affected
threats, controls and context updates for the authorized remediation work.

Trace relevant input, trust boundaries and consequences. Use safe isolated
reproductions for credible findings. Record prerequisites, attacker-controlled
input, affected behavior, impact, evidence, remediation and a check that
distinguishes vulnerable from fixed behavior. Separate hypotheses from validation.

Use available native or specialist tools appropriate to the task. This skill
does not bundle a scanner, security plugin, model entitlement or persistent monitor.
Do not claim a tool was used when it was unavailable. A completed scan is not
proof of absence; a compiling patch is not proof of remediation.

Keep sensitive findings private. Convert accepted remediation into a bounded
development task with its own tests and independent review. Incident containment,
production changes and external disclosure follow their explicit authority and
recovery rules. Retain prior delegation without silently expanding the target.

Return validated findings, inconclusive claims, relevant remediation checks and
remaining exposure. State the precise coverage; do not generalize one test into
a guarantee that the application or host is secure.
