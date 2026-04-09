---
name: cfd-rca-debugger
description: Use when debugging a customer-found defect and identifying likely root cause from message text, Jira tickets, docs, source code, logs, dashboards, and monitor evidence.
version: 1.2.0
risk: medium
evidence:
  outputs:
    - ai/rca/CFD_RCA_NOTES.md
    - ai/rca/QUERY_LOG.md
    - ai/rca/ROOT_CAUSE_REPORT.md
    - ai/rca/FIX_RECOMMENDATIONS.md
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
---

# CFD RCA Debugger

Use this skill for evidence-backed debugging of BAP customer-found defects.

This skill is for customer-reported defects where the best source of truth varies by issue:
- some CFDs are doc-driven
- some are source-code or config-driven
- some need Splunk
- some need ops, terraform, or deployment context
- some benefit from checking matching external-monitor evidence after the issue is scoped

## Inputs To Capture First

- Raw user-reported symptom or error text.
- Environment, app, resource, and timeframe.
- Any Jira link, attachment, screenshot, or reproduction steps.
- Any request ID, correlation ID, user ID, org ID, external FQDN, or test URL.
- Any relevant dashboard, synthetic result, or detector link if one already exists for the same user flow.
- Recent changes if already known.

## Entry Point Types

Classify the starting point before deep debugging:
- `customer-symptom`: only symptom text, screenshot, or reproduction details are available
- `jira-backed`: issue description, comments, or attachments contain the best context
- `request-or-log-backed`: the engineer already has request IDs, log signatures, or time windows
- `signal-corroborated`: there is an internal or external monitor that validates the same user flow
- `code-regression`: the issue appears tied to a feature change, release, or source-code path

## Workflow

1. Normalize the intake.
   - Restate the problem in one sentence.
   - Extract environment, timeframe, app/resource, and the best available error signatures.
2. Read `docs/architecture.md` and `references/cfd-intake-playbook.md`.
   - Map the symptom to likely owning components and likely first evidence sources.
3. Scan `ai/rca/CFD_RCA_NOTES.md` for matching prior patterns.
   - Use it as compact hypothesis memory, not as proof.
   - Keep looking for direct evidence in docs, code, tickets, logs, or runtime config.
4. Pull issue-specific context first.
   - If a Jira link or attachment exists, read `references/jira-playbook.md`.
   - If the message itself contains stack traces, HTTP errors, screenshots, or reproduction steps, treat those as first-class evidence.
5. Pull design and feature context.
   - Use `docs/confluence_playbook.md`.
   - Prefer product design docs before deep log or code analysis.
6. Pull source-code context.
   - Read `references/repo-paths.md` and `references/source-code-playbook.md`.
   - Sync relevant repos before code-level debugging with `./scripts/sync_repos.py` or `./scripts/prepare_repo_context.sh`.
   - Start with the most likely owning repo, then inspect adjacent components in the request path.
7. Pull runtime-config and deployment context where needed.
   - Read `references/deployment-context-playbook.md`.
   - Use ops, terraform, and release-info when the issue may depend on config, platform wiring, supported ciphers, or rollout timing.
   - For intermittent post-deploy auth failures or node-specific callback/login errors, verify sync completion and node-local rules state before assuming an application bug.
8. Pull observability evidence only where needed.
   - Use `references/splunk-playbook.md` for time-bounded log evidence.
   - Use `references/signalfx-synthetics-playbook.md` when a matching synthetic or external monitor can corroborate the same user flow.
   - If a Nidz check is relevant, inspect the Nidz API repo and correlate the check implementation with product code paths.
9. Build 2-3 hypotheses.
   - Each hypothesis must be tied to a specific signal, code path, document, or error signature.
10. Confirm or reject hypotheses with explicit evidence.
   - Do not call something root cause from one weak signal.
   - Separate hard evidence from inference.
11. Produce RCA outputs in `ai/rca/`.
   - `CFD_RCA_NOTES.md`: persistent compact knowledge base for future debugging
   - `QUERY_LOG.md`: per-investigation queries, filters, and rationale
   - `ROOT_CAUSE_REPORT.md`: per-investigation concise final RCA
   - `FIX_RECOMMENDATIONS.md`: per-investigation engineering follow-up and validation steps
12. Update `ai/rca/CFD_RCA_NOTES.md` only when the investigation reveals new reusable knowledge.
   - Add one short entry after the lesson is evidence-backed enough to help later debugging.
   - Keep entries tiny and searchable: pattern, telltale signals, and best verification or fix direction.
   - Do not store customer names, ticket-only timelines, raw query text, or long narratives there.
   - Merge with an existing note instead of adding a near-duplicate.
13. If evidence is still insufficient, stop with a clear gap statement.
   - State exactly what is missing and the next best source to query.

## Guardrails

- No Source code changes unless Engineer explicitly asks you to modify something.
- Do not assume Splunk is always the first step.
- Do not assume every CFD has a matching monitor or synthetic.
- Do not guess root cause from a repo name, feature name, or Jira title alone.
- Do not jump to rollback or mitigation unless the user explicitly asks for operational guidance.
- Prefer feature documents, code paths, runtime config, and issue-specific evidence over generic dashboards when they conflict.
- Treat `ai/rca/CFD_RCA_NOTES.md` as compact memory, not a dump of every investigation.

## Source Priority By Situation

- User-reported symptom with clear error text:
  - message text
  - `ai/rca/CFD_RCA_NOTES.md` for prior patterns
  - architecture docs
  - owning repo
  - Splunk or Jira as needed
- Jira-backed CFD:
  - Jira description, comments, and attachments
  - `ai/rca/CFD_RCA_NOTES.md` for prior reusable patterns
  - Confluence docs
  - owning repo
  - logs or signals as validation
- CFD with matching external monitor in place:
  - customer symptom first
  - SignalFx or synthetic evidence as corroboration
  - architecture docs
  - relevant repo
  - Splunk for request-path confirmation
- Runtime-config or platform-specific CFD:
  - feature docs
  - source repo
  - ops or terraform
  - release and deployment context
- Intermittent login or callback failures after deploy:
  - `ai/rca/CFD_RCA_NOTES.md` for prior auth-broker and sync patterns
  - source repo for the callback or cookie path
  - ops startup gating and sync completion
  - Splunk grouped by host
  - release context only if the symptom is wave-specific
- Suspected regression:
  - feature docs
  - source repo
  - release or recent change context
  - logs only to confirm behavior

## Completion Criteria

- Scope is clearly restated.
- Candidate owning component(s) are identified.
- Evidence sources are listed explicitly.
- Top hypotheses are tested and narrowed.
- A likely root cause or the tightest current explanation is stated.
- Confidence and remaining unknowns are explicit.
- Engineering follow-up is specific and testable.
