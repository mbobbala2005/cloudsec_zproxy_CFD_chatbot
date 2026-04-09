---
name: bap-query-resolver
description: Use when answering BAP architecture, product behavior, feature-support, or implementation questions such as whether a feature is supported, how a request path works, which repo owns behavior, which ciphers or timeouts apply, or where the implementation can be verified.
version: 1.0.0
risk: low
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
---

# BAP Query Resolver

Use this skill for BAP architecture and product-implementation questions.

The examples in this skill are representative, not exhaustive.

This skill is for questions such as:
- does BAP support this behavior or feature
- how was a feature implemented
- which component owns a request-path phase
- what Envoy handles on the upstream or downstream side
- which ciphers or timeout settings apply
- which repo, config, or document should be used to verify an answer

## Inputs To Capture First

- The exact user question.
- Any feature name, app type, private-resource detail, or config knob named in the question.
- Whether the user is asking about:
  - documented support
  - current implementation
  - environment-specific runtime behavior
  - ownership or repo location
- Any Jira ticket, PR, design-doc term, or repo path already mentioned.

## Question Types

Classify the question before exploring:
- `feature-support`: "Do we support this?"
- `feature-implementation`: "How is this implemented?"
- `request-path-behavior`: "Which component handles this flow?"
- `runtime-behavior`: "Which ciphers, idle timeouts, routing, or config values apply?"
- `ownership`: "Which repo or service owns this?"
- `documentation-gap`: "I do not see this in docs; is it supported or just undocumented?"

## Workflow

1. Normalize the question.
   - Restate it in one sentence.
   - Identify whether the user needs product behavior, implementation detail, or runtime-config detail.
2. Read `docs/architecture.md`, `docs/repo_links.md`, and `references/query-intake-playbook.md`.
   - Map the question to likely owning components and the best first evidence source.
3. Pull product and feature context first.
   - Use `references/securitydocs_playbook.md` when the question is about documented support, exposed options, limits, or customer-visible behavior.
   - Use `docs/confluence_playbook.md` for Confluence retrieval.
   - Use `.agents/skills/cfd-rca-debugger/references/jira-playbook.md` if the question is backed by a ticket or internal doc.
4. Pull implementation detail when the answer is not obvious from docs.
   - Read `references/feature-implementation-playbook.md`.
   - Sync the relevant repos before using local source as evidence.
   - Use `.agents/skills/cfd-rca-debugger/references/repo-paths.md` and `.agents/skills/cfd-rca-debugger/references/source-code-playbook.md`.
5. Pull runtime-config context when the answer depends on how the product is actually deployed.
   - Read `references/runtime-behavior-playbook.md`.
   - Use `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`.
6. Use observability only when it adds value.
   - Splunk is useful for log vocabulary or field names.
   - SignalFx is useful for dashboards or metric naming.
   - Neither should be the first step for most product queries.
7. Answer with a concise, engineer-friendly result.
   - Say the answer directly.
   - Name the owning component or repo.
   - Say where the behavior is implemented or configured.
   - State any confidence or documentation gap clearly.

## Guardrails

- No source-code changes unless the engineer explicitly asks for implementation work.
- Do not turn a product question into RCA unless the user is asking why a customer-facing failure happened.
- Do not assume missing user docs means the feature is unsupported.
- Do not assume code presence alone means the behavior is enabled in every environment.
- For ciphers, timeouts, routing, or other runtime knobs, check both implementation and deployment context before answering definitively.
- If different layers may own the answer, call out each layer instead of collapsing them into one guess.

## Source Priority By Question

- Feature support or semantics:
  - architecture docs
  - official support docs
  - Confluence
  - owning repo
  - deployment context if behavior may vary by environment
- Feature implementation:
  - feature docs
  - owning repo
  - adjacent repo in the request path
  - ops or terraform when config shapes behavior
- Envoy upstream or downstream behavior:
  - architecture docs
  - Envoy repo
  - Envoy Controller repo
  - Auth-Broker if auth flow affects the answer
- Runtime questions such as accepted ciphers or idle timeout:
  - source repo
  - ops or terraform
  - release and deployment context
  - docs for terminology or expected behavior
- Documentation-gap questions:
  - docs first
  - official support docs
  - implementation second
  - answer whether the behavior appears implemented, configurable, documented, or still unclear

## Representative Example Questions

- Do we support multiple destinations for a BAP private resource?
- Which upstream and downstream connections does Envoy handle in the BAP path?
- Which ciphers are accepted by BAP?
- What is the idle timeout in BAP?
- Which repo should I read to understand how app portal/CORS was implemented?
- Which component decides whether a browser-based private-access request is allowed or blocked?
- Is this limitation documented for customers, or is it only visible in implementation?
- Where is private-resource selection or routing behavior defined?

## Completion Criteria

- The question is answered directly.
- The likely owning component(s) are named.
- The answer distinguishes documented behavior from implementation detail when needed.
- Runtime-config dependencies are called out when relevant.
- The best verification source is included.
- Any confidence gap or missing document is stated explicitly.
