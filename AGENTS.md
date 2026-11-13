# Contributor instructions

Revision: 0.2.0 · Updated: 2026-11-13

Read [VISION.md](VISION.md), [README.md](README.md) and the affected skill.
Read [system.yaml](system.yaml) and [source ownership](docs/system-definition.md) for the selected exported declaration and owning sources. The Notion YAML block owns the current authoring definition; use a release/export at its recorded revision when working from that version. Do not silently refresh it mid-task or edit a distribution as a second original. The declaration is interpreted by the working project agent; it does not apply settings, grant authority or override holds.
This repository owns versioned distributions and Agentic System Lab's native project artifacts, not an adopting application's product rules. Shared methods are authored in the linked Notion home; existing bundles retain authority for their released versions until reviewed cutover.

Keep one canonical source for each skill and its references. A staged bundle
must remain useful outside this checkout. Put required resources inside its
skill folder; do not link to a personal plugin or another checkout.

Prefer the selected native agent tools, workspace and project services. A new helper must have a concrete
setup or validation responsibility and bounded effects. Do not add runtime
orchestration, a provider registry, a dashboard or an execution store.

Preserve the two decision points and explicit scoped delegation. An external
issue, model response or skill never grants authority by itself. Keep secrets,
native history, machine identities and raw security findings out of this repo.

Run `python3 scripts/check.py` and `python3 -m unittest discover -s tests`.
Material skill changes need representative behavioral evidence; metadata checks
alone cannot prove decisions. Review the final candidate independently before
authorized delivery. Record live proof separately from fixtures and source review.

Keep technical changes, tasks and proof in the selected native tracker/repository; update shared method/context in its owning source. Avoid a second editable copy. Update affected guides, README roadmap and the
qualification record when the accepted work changes their claims. Preserve dates of actual observations. Readback published artifacts and preserve a recovery path;
do not turn a passing package check into an installation claim.

Follow the revision convention in CONTRIBUTING when editing skills or Markdown.
Keep edit dates separate from dates of observed behavior. Preserve the human Git
author and actual contributors' native Co-authored-by trailers through delivery;
do not credit a model for work it did not perform.
