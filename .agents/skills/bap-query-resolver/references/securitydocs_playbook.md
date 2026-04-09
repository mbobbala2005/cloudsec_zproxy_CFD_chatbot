# Cisco Secure Access Support Docs Playbook

Use this playbook for official Cisco Secure Access help content that is relevant to BAP queries.

## Purpose

This source is useful when the agent needs to answer:
- whether a BAP-related capability is officially documented
- what options or workflows are exposed to customers in Secure Access
- what the support docs say about private resources, browser-based zero trust access, application portal, or timeout behavior
- whether a question is a documentation gap versus an implementation question

## Scope Guardrail

This documentation set covers many Cisco Secure Access sub-products.

For this repo, use it only for BAP-relevant material such as:
- private resources and private access rules
- browser-based zero trust access
- application portal
- timeout intervals for zero trust access sessions
- other BAP-adjacent configuration, limits, prerequisites, and supported workflows

## Entry Point

Main documentation map:
- `https://securitydocs.cisco.com/docs/csa/olh/118708.ditamap`

This page is the Cisco Secure Access Help book index and includes BAP-relevant sections such as:
- `Hybrid Private Access Workflow`
- `Private Resources`
- `Application Portal for Zero Trust Access Browser-Based User Access`
- `Timeout Intervals for Zero Trust Access Sessions`

## Examples Of Useful BAP-Relevant Pages

- `Timeout Intervals for Zero Trust Access Sessions`
  - `https://securitydocs.cisco.com/docs/csa/olh/120002.dita`
- `Application Portal for Zero Trust Access Browser-Based User Access`
  - `https://securitydocs.cisco.com/docs/csa/olh/119968.dita`
- `Configure an Application Portal for Zero Trust Access Browser-Based User Access`
  - `https://securitydocs.cisco.com/docs/csa/olh/119991.dita`
- `Configure Browser-Based Zero Trust Access to Private Resources`
  - `https://securitydocs.cisco.com/docs/csa/olh/119979.dita`
- `Manage Private Resources`
  - `https://securitydocs.cisco.com/docs/csa/olh/118903.dita`
- `Define a Private Resource`
  - `https://securitydocs.cisco.com/docs/csa/olh/120574.dita`

## How To Use This Source

1. Start here when the question is about documented product behavior or customer-visible configuration.
2. Use it before source-code tracing when the question sounds like:
   - "Do we support this?"
   - "Is this documented?"
   - "What options does the UI expose?"
   - "What do customers configure for this feature?"
3. If the docs are silent or ambiguous, move to:
   - `docs/confluence_playbook.md`
   - `docs/repo_links.md`
   - `.agents/skills/cfd-rca-debugger/references/source-code-playbook.md`
   - `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`
4. Answer clearly whether the result came from:
   - official support docs
   - internal design docs
   - implementation
   - runtime configuration

## Best-Fit Question Types

- feature support
- documentation gaps
- private-resource configuration semantics
- application portal behavior
- browser-based user flows
- timeout or range-limit questions

## Caution

Do not assume the support docs fully describe internal implementation details.

They are strongest for:
- documented capabilities
- exposed configuration choices
- limitations and prerequisites

They are weaker for:
- exact handler or function ownership
- environment-specific runtime values
- internal design decisions not exposed to customers
