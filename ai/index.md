# AI Task Routing

Use this map to choose the right workflow quickly.

## Product Knowledge Questions

Use this path for:
- component behavior
- architecture explanations
- ownership and repo lookups
- feature support and semantics questions
- implementation-detail questions such as ciphers, idle timeout, or multiple destinations
- "where should I look" questions

Primary workflow:
- `.agents/skills/bap-query-resolver/SKILL.md`

Preferred sources:
- `docs/architecture.md`
- `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`
- `docs/repo_links.md`
- `docs/knowledge_sources.md`
- `ai/system_prompt.md`
- `.agents/skills/bap-query-resolver/references/query-intake-playbook.md`
- `.agents/skills/bap-query-resolver/references/feature-implementation-playbook.md`
- `.agents/skills/bap-query-resolver/references/runtime-behavior-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/repo-paths.md`
- `.agents/skills/cfd-rca-debugger/references/source-code-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/jira-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/confluence-playbook.md`

## CFD RCA Questions

Use this path for:
- debugging a CFD from an error message
- tracing a symptom to the likely component
- using Jira, Confluence, GitHub, Splunk, SignalFx, ops, terraform, or deployment context as RCA evidence
- validating or rejecting root-cause hypotheses

Primary workflow:
- `.agents/skills/cfd-rca-debugger/SKILL.md`

Preferred sources:
- `ai/rca_system_prompt.md`
- `ai/rca/CFD_RCA_NOTES.md`
- `.agents/skills/cfd-rca-debugger/references/cfd-intake-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/source-code-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/jira-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/splunk-playbook.md`
- `.agents/skills/cfd-rca-debugger/references/signalfx-synthetics-playbook.md`

## Observability Context

Use this path when the user asks for:
- which Splunk area is relevant
- which SignalFx dashboard is relevant
- how to verify a product behavior

Guardrail:
- provide context and likely verification paths
- use dashboards and synthetics as corroboration, not as the default starting point for a CFD

## Knowledge Gap Handling

Use this path when the current repo cannot answer the question confidently.

Expected output:
- what is known
- what is missing
- which future source should be connected next, such as Confluence

## Add New Knowledge

When new information is broadly reusable:
1. Update `docs/architecture.md`, `docs/repo_links.md`, or `docs/knowledge_sources.md`.
2. Update `ai/system_prompt.md` or `.agents/skills/bap-query-resolver/**/*` when architecture-query behavior should change.
3. Update `ai/rca_system_prompt.md` or `.agents/skills/cfd-rca-debugger/**/*` when RCA behavior should change.
4. Keep compact reusable RCA patterns in `ai/rca/CFD_RCA_NOTES.md`.
5. Keep full case-specific evidence in per-investigation artifacts, not in `ai/rca/CFD_RCA_NOTES.md`.
