# Feature Implementation Playbook

Use this playbook when the question is really asking how a BAP feature works in implementation, not just which component owns it.

The question families below are representative, not exhaustive.

## Goal

Answer implementation questions with enough precision that another engineer knows:
- which service owns the behavior
- which source path or config path matters
- whether the answer is documented, implemented, configurable, or still unclear

## Workflow

1. Identify the feature term or behavior.
2. Find the relevant product or design context first.
   - `docs/architecture.md`
   - `references/securitydocs_playbook.md`
   - `.agents/skills/cfd-rca-debugger/references/confluence-playbook.md`
   - Jira when the question is backed by a ticket, linked doc, or rollout note
3. Map the feature to the request path.
   - decide which component is primary
   - note adjacent components that may shape the behavior
4. Trace the implementation.
   - sync the relevant repos first with `./scripts/sync_repos.py` or `./scripts/prepare_repo_context.sh`
   - use `.agents/skills/cfd-rca-debugger/references/repo-paths.md`
   - use `.agents/skills/cfd-rca-debugger/references/source-code-playbook.md`
5. If runtime config may change the answer, cross-check:
   - `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`
6. Answer in terms of:
   - direct answer
   - owning component
   - implementation or config location
   - best verification source
   - documentation gap, if any

## Representative Question Families

### Resource Modeling And Destination Semantics

Do not stop at public or user docs if they are silent.

Check:
- feature docs or resource-model docs
- the source path that resolves private-resource destinations
- whether the behavior is per-request, per-connection, or per-session
- whether routing or destination selection is shaped by Auth-Broker, Envoy Controller, or deployment config

Examples:
- multiple destinations for a private resource
- private-resource groups, addresses, ports, or selection semantics

### Request-Path Ownership And Connection Handling

Check:
- the high-level request flow in `docs/architecture.md`
- Envoy auth filter, routing, and MT-proxy related code
- Envoy Controller when the answer depends on xDS-programmed listeners, routes, clusters, or filter chains
- Auth-Broker when auth, policy, cookie, or callback behavior shapes the answer

Examples:
- upstream or downstream handling in Envoy
- which component owns a given request-path phase
- how browser-based access reaches the target application

### Security And TLS Behavior

Check:
- TLS-related source config in the primary proxy layer
- OPS and Terraform for rendered or deployed values
- environment-specific rollout context if the answer may differ by platform or wave

Examples:
- accepted ciphers
- TLS behavior
- certificate or handshake behavior

### Session, Timeout, And Lifecycle Behavior

Check:
- Envoy listener, route, cluster, or stream timeout configuration
- Auth-Broker session or cookie lifetime if the question is really about session expiry
- OPS and Terraform for environment overrides or deployed values

Examples:
- idle timeout
- session timeout
- long-lived browser or websocket behavior

### Policy, Access, And Reporting Behavior

Check:
- architecture flow
- Auth-Broker policy and login-callback behavior
- Policy Broker or Policy Gen when enforcement logic matters
- logging or reporting code paths when the question is about what users see in activity search or dashboards

Examples:
- why access is blocked or allowed
- which component owns policy evaluation
- why a dashboard or activity view shows a certain semantic

### Application Portal And Browser Experience

Check:
- official support docs first
- feature docs
- Auth-Broker and Envoy behavior
- source code only after the high-level flow is clear

Examples:
- what application portal supports
- how browser-based access is exposed to users
- whether a behavior is customer-visible, configurable, or implementation-only

## Evidence Rules

- Prefer concrete file paths, handlers, config keys, or design docs over broad summaries.
- Distinguish between code support and deployed behavior.
- Distinguish between user-facing documentation and internal implementation truth.
