# BAP CFD Agent Workspace

BAP agent workspace for:
- architecture and product knowledge Q&A
- CFD root-cause analysis workflows and playbooks

## Purpose

This repo is for BAP-aware agents with two modes:
- `Architecture`: product knowledge, ownership, repo lookup, flow explanation
- `RCA`: debug customer-found defects using docs, code, logs, tickets, ops, terraform, deployment context, and corroborating monitor context when useful

The assistant should help escalation engineers answer questions such as:
- what a component does
- which repo owns a behavior
- how authentication and authorization flow works
- where to look in Splunk or SignalFx for product context
- which architecture documents or source repos are relevant
- how to debug a CFD when the engineer has only an error message, Jira ticket, or partial evidence
- how to debug a CFD where source code, ops, terraform, or deployment context matter more than logs
- how to validate user-facing issues against matching external monitors when those monitors exist

The current repo scope is context, prompts, skills, playbooks, and lightweight repo-access helpers for deployment.

## Non-Goals

This repo should not be treated as:
- a live outage command workflow
- a remediation or rollback automation tool
- a place to encode one-off CFD details into shared instructions

## Initial Knowledge Sources

- Product architecture: `docs/architecture.md`
- Canonical component repos: `docs/repo_links.md`
- Source access patterns and observability guardrails: `docs/knowledge_sources.md`
- Cisco Secure Access support docs access pattern: `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`
- Confluence access and search patterns: `.agents/skills/cfd-rca-debugger/references/confluence-playbook.md`
- AI workflow routing: `ai/index.md`
- Architecture prompt: `ai/system_prompt.md`
- Query skill and playbooks: `.agents/skills/bap-query-resolver/`
- RCA prompt: `ai/rca_system_prompt.md`
- RCA skill and playbooks: `.agents/skills/cfd-rca-debugger/`

## Planned Knowledge Sources

The repo is intentionally ready for richer RCA retrieval as more sources become available:
- Confluence spaces for detailed architecture and design docs
- Jira tickets and attachments for issue-specific evidence
- Additional product runbooks and FAQ content

## Repo Access For Deployment

For repo-backed answers on a deployed Ubuntu instance:
- set `APP_ID`, `PRIVATE_KEY_PATH`, and preferably `INSTALLATION_ID` in `.env`
- run `./scripts/prepare_repo_context.sh` before repo-backed analysis starts
- use `./scripts/sync_repos.py --repo <ENV_VAR>` when only one repo family is needed

The sync helper will clone missing repos, fast-forward existing ones, and stop if a local worktree is dirty or cannot fast-forward cleanly.

## Suggested Answer Style

For architecture questions, answers should usually include:
1. A direct answer in 2-4 sentences.
2. The relevant component or subsystem.
3. Where that behavior lives, such as a repo, dashboard, or document.
4. Any confidence note or knowledge gap if the answer is incomplete.

For RCA questions, outputs should usually include:
1. Scope and symptom summary.
2. Evidence gathered and source list.
3. Top hypotheses tested.
4. Most likely root cause and confidence.
5. Recommended engineering follow-up.

## Repository Layout

- `AGENTS.md`: operating guide for the assistant
- `ai/index.md`: task routing
- `ai/system_prompt.md`: architecture-mode system prompt
- `.agents/skills/bap-query-resolver/`: architecture and product-implementation query skill
- `ai/rca_system_prompt.md`: RCA-mode system prompt
- `ai/rca/README.md`: RCA artifact conventions
- `docs/architecture.md`: BAP architecture notes
- `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`: official Cisco Secure Access support-doc usage for BAP queries
- `.agents/skills/cfd-rca-debugger/references/confluence-playbook.md`: Confluence API access, search patterns, and examples
- `docs/repo_links.md`: canonical GitHub repo links
- `docs/knowledge_sources.md`: GitHub, Splunk, SignalFx, Confluence, and Jira guidance
- `.agents/skills/cfd-rca-debugger/`: CFD RCA skill and source-specific playbooks
- `scripts/github_auth.py`: GitHub App auth helper for `git` and `gh`
- `scripts/sync_repos.py`: sync or clone all configured repos before repo-backed analysis
- `scripts/prepare_repo_context.sh`: source `.env` and sync configured repos
- `.env.example`: starter env vars for future integrations
