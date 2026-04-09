# AI Agent Operating Guide

This repository is configured for BAP-aware agents with two modes:
- `Architecture`: product knowledge and ownership questions
- `RCA`: customer-found defect debugging and evidence-backed root-cause analysis

## Purpose

- Help the escalation team answer product and architecture questions quickly.
- Provide reusable RCA workflows for debugging CFDs from logs, docs, code, tickets, ops, terraform, deployment context, and corroborating monitor evidence.
- Keep answers grounded in reusable documentation and source-of-truth repos.
- Turn repeated CFD questions into durable knowledge that can be reused by the team.

## Non-Goals

- Do not treat this repo as a live outage command workflow.
- Do not default to rollback, mitigation, `OOR`, or silence guidance.
- Do not present observability data as proof of root cause unless the evidence is explicit and cross-checked.

## Source Of Truth

- Canonical instructions: `AGENTS.md`
- Task routing: `ai/index.md`
- Product architecture: `docs/architecture.md`
- Official support docs: `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`
- Canonical repos: `docs/repo_links.md`
- Knowledge source rules: `docs/knowledge_sources.md`
- Architecture response contract: `ai/system_prompt.md`
- Architecture query skill: `.agents/skills/bap-query-resolver/SKILL.md`
- RCA response contract: `ai/rca_system_prompt.md`
- RCA skill: `.agents/skills/cfd-rca-debugger/SKILL.md`

## Default Workflow For An Architecture Question

When asked a CFD or product knowledge question, follow this order:
1. Identify the question type: architecture, ownership, behavior, repo lookup, observability lookup, or documentation gap.
2. Answer directly and concisely first.
3. Use `.agents/skills/bap-query-resolver/SKILL.md` and its references to choose the best first evidence source for the question.
4. Ground the answer in the existing docs in this repo before using external sources.
5. Use official Cisco Secure Access support docs for documented product behavior, options, and limitations when they are relevant to BAP.
6. Use Confluence when the question is feature-specific or asks how something was implemented.
7. Before relying on local repo evidence, sync the relevant repos to latest remote state.
8. Use GitHub repo context when docs are too high level or missing.
9. Use ops, terraform, and release-info context when the question is really about runtime behavior such as ciphers, timeouts, routing, or environment-specific behavior.
10. Use Splunk or SignalFx for product context, vocabulary, dashboards, or known signal locations, not as the default first step.
11. If the question requires live operational coordination, say that this repo is for architecture and CFD debugging, not outage coordination.
12. End with the best verification source, such as a repo, architecture section, support-doc page, config path, or Confluence page.

## Default Workflow For An RCA Question

When asked to debug a CFD or identify root cause, follow this order:
1. Capture the raw intake first: user message, error text, Jira link, screenshot, attachment, environment, timeframe, and affected app or component.
2. Classify the starting point:
   - customer symptom with only message-level context
   - Jira-backed issue
   - request ID or log-backed investigation
   - corroborating monitor or synthetic evidence available
   - suspected regression or code-path issue
3. Read `docs/architecture.md` and use `.agents/skills/cfd-rca-debugger/references/cfd-intake-playbook.md` to map the symptom to likely components and first sources.
4. Briefly scan `ai/rca/CFD_RCA_NOTES.md` for matching prior patterns, but treat it as hypothesis memory rather than proof.
5. Use Confluence for design and feature context before doing deep code or log analysis.
6. Use Jira when ticket descriptions, screenshots, comments, or attachments contain issue-specific evidence.
7. Sync the relevant repos before using local source as evidence.
8. Use GitHub and local repos for code-level tracing, runtime-config tracing, and recent change analysis.
9. Use ops, terraform, and release-info context when the issue may depend on runtime config, platform wiring, cipher support, routing behavior, or a recent deployment wave.
10. Use Splunk and SignalFx only as evidence sources, not as the default starting point for every CFD.
11. Build 2-3 evidence-backed hypotheses and explicitly confirm or reject each.
12. Produce a structured RCA with evidence, likely root cause, confidence, and recommended engineering follow-up.
13. If the investigation reveals new durable debugging knowledge, append one very short reusable note to `ai/rca/CFD_RCA_NOTES.md`.
14. If evidence is insufficient, state the missing data clearly instead of guessing.

## Response Style

- Optimize for outputs another engineer can use immediately.
- Prefer direct explanations over long analysis.
- Call out uncertainty instead of guessing.
- Separate product behavior from operational action.
- If there is a knowledge gap, say exactly which document or team-owned source would close it.
- For RCA, separate confirmed evidence from hypotheses and unknowns.

## GitHub Usage Guardrails

- Treat `docs/repo_links.md` as the canonical list of repos.
- Use GitHub repos for:
  - component ownership
  - README and design doc discovery
  - implementation lookup when product docs are incomplete
  - mapping behavior to the responsible service
- Before using a local repo as evidence, sync it to latest remote state.
- On deployed or unattended hosts, use `scripts/prepare_repo_context.sh` or `scripts/sync_repos.py`.
- When `APP_ID` and `PRIVATE_KEY_PATH` are set, use the GitHub App helper in `scripts/github_auth.py` for repo access.
- If a repo cannot fast-forward cleanly, stop instead of reasoning from stale local state.
- Avoid proposing code changes unless the user explicitly asks for implementation work.

Expected environment variables:
- `APP_ID`
- `PRIVATE_KEY_PATH`
- `INSTALLATION_ID`
- `GITHUB_BASE_URL`
- `GITHUB_API`

## Splunk Usage Guardrails

- Use environment variables for credentials.
- Use Splunk to find:
  - request-path evidence
  - correlation IDs
  - runtime error signatures
  - whether a symptom appears in the relevant timeframe
- Do not frame Splunk as the primary tool unless the issue is clearly log-driven.
- Do not treat ad hoc log evidence alone as a full RCA.

Expected environment variables:
- `SPLUNK_BASE_URL`
- `SPLUNK_TOKEN`
- `SPLUNK_APP`
- `SPLUNK_DEFAULT_INDEX`

## SignalFx Usage Guardrails

- Use SignalFx for component dashboards, health signals, topology context, and synthetic corroboration.
- Use it to answer questions such as:
  - whether a user-facing issue is also visible in the same DC or path
  - which synthetic step failed
  - whether a failure looks persistent or transient
- Do not use SignalFx as a substitute for architecture docs or code tracing.
- Do not assume a matching monitor exists for every CFD.

Expected environment variables:
- `SIGNALFX_BASE_URL`
- `SIGNALFX_API_TOKEN`

## Confluence And Jira

When access is available, prefer them for:
- detailed architecture decisions
- sequence diagrams
- release notes
- operational FAQs
- cross-team design discussions
- issue-specific ticket evidence
- screenshots and attachments tied to a CFD

## Ops, Terraform, And Release Context

Use these repos when the CFD may depend on:
- runtime config rather than application logic
- cipher suites, TLS knobs, or proxy wiring
- routing behavior, listeners, or platform-specific network setup
- latest deployments, waves, promotions, or regression timing

Read:
- `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`

Expected environment variables:
- `CONFLUENCE_BASE_URL`
- `CONFLUENCE_USER`
- `CONFLUENCE_API_TOKEN`
- `CONFLUENCE_SPACE_KEYS`
- `JIRA_BASE_URL`
- `JIRA_USER`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEYS`

## Local Repository Paths For Query And RCA

Expected environment variables:
- `REPO_BASE_DIR`
- `NIDZ_API_REPO_PATH`
- `AUTH_BROKER_REPO_PATH`
- `ENVOY_REPO_PATH`
- `ENVOY_CONTROLLER_REPO_PATH`
- `POLICY_BROKER_REPO_PATH`
- `POLICY_GEN_REPO_PATH`
- `GUACD_REPO_PATH`
- `GUACAMOLE_LITE_REPO_PATH`
- `TERRAFORM_REPO_PATH`
- `OPS_REPO_PATH`
- `RELEASE_INFO_REPO_PATH`

Recommended sync commands:
- `./scripts/prepare_repo_context.sh`
- `./scripts/sync_repos.py --repo AUTH_BROKER_REPO_PATH`

## Knowledge Update Policy

- Update shared docs when a new answer would likely be reused.
- Prefer adding durable architecture or ownership knowledge over one-off case notes.
- Keep one-off case details or customer-specific details out of the shared product knowledge docs unless the lesson is broadly reusable.
- Keep RCA playbooks generic and reusable; do not bake a single CFD's private details into shared skill instructions.
- Use `ai/rca/CFD_RCA_NOTES.md` as compact RCA memory for reusable debugging patterns only.
- Keep `ai/rca/CFD_RCA_NOTES.md` short and searchable by storing only brief evidence-backed lessons, not full case notes.

## Documentation Layout

- `ai/index.md`: task routing map
- `ai/system_prompt.md`: architecture assistant instructions
- `.agents/skills/bap-query-resolver/`: architecture and implementation-query workflow
- `ai/rca_system_prompt.md`: RCA assistant instructions
- `.agents/skills/cfd-rca-debugger/`: RCA workflow and source-specific playbooks
- `docs/architecture.md`: product architecture
- `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`: official Cisco Secure Access support-doc guidance
- `docs/repo_links.md`: canonical repo URLs
- `docs/knowledge_sources.md`: access and source guidance

## Change Management

- Update `AGENTS.md` when the agent scope or guardrails change.
- Update `docs/architecture.md` when component responsibilities or flows change.
- Update `docs/repo_links.md` when canonical repos change.
- Update `docs/knowledge_sources.md` when new document systems or observability tools are added.
- Update `.agents/skills/bap-query-resolver/**/*` when architecture or implementation-query workflow improves.
- Update `.agents/skills/cfd-rca-debugger/**/*` when RCA workflow or evidence sources improve.
