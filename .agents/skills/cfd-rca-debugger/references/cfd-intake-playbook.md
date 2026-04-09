# CFD Intake Playbook

Use this playbook to start RCA from whatever evidence the engineer already has.

## Goal

Turn a vague CFD report into:
- a normalized problem statement
- likely owning components
- the best first evidence sources

## Intake Checklist

Capture these before deep debugging:
- exact error text, stack trace, HTTP status, or screenshot text
- environment and timeframe
- affected app, external FQDN, or internal destination
- user, org, request, or correlation identifiers if available
- reproduction steps
- any Jira link, comment, screenshot, or attachment
- any dashboard, synthetic result, or detector link that matches the same user flow

## Starting Point Classification

### Customer Symptom

Use this when the engineer only has message-level context such as:
- browser error message
- screenshot
- HTTP status
- short symptom description

Start with:
- `docs/architecture.md`
- symptom-to-component mapping below
- Confluence feature docs
- owning repo after the likely component is identified

### Jira-Backed

Use this when a Jira ticket contains the richest context.

Start with:
- issue description and comments
- attachments and screenshots
- reproduction steps
- linked feature documents

### Log-Backed

Use this when the engineer already has a request ID, exact log signature, or narrow time window.

Start with:
- Splunk
- architecture docs
- relevant repo and code path

### Signal-Corroborated

Use this when a matching internal or external monitor exists for the same user-facing flow.

Start with:
- the user symptom first
- the matching synthetic result or detector evidence
- then correlate the monitor result with product docs, code, logs, and runtime context

## Symptom-To-Component Clues

- login redirect loops, missing cookie, JWT issues, callback failures:
  - start with `Auth-Broker`
  - adjacent components: `Envoy`, `Federation Gateway`
- intermittent `400` after SSO, callback loops on some nodes only, missing org or rule-hash symptoms:
  - start with `Auth-Broker`
  - adjacent components: `Syncer Client`, `OPS`, `Federation Gateway`
- xDS, route, listener, websocket, cluster, filter-chain issues:
  - start with `Envoy Controller`
  - adjacent component: `Envoy`
- policy allow or deny mismatches, block page behavior, IPS or DLP gating:
  - start with `Auth-Broker`
  - adjacent components: `Policy Broker`, `Policy Gen`
- RDP, SSH, websocket bridge, token, or proxy-protocol issues:
  - start with `Guacd` or `Guacamole-lite`
  - adjacent components: `Auth-Broker`, `Envoy`
- certificate, SNI, TLS handshake, or cert retrieval issues:
  - start with `Enclave`
  - adjacent component: `Envoy`
- monitor-only failures or check implementation questions:
  - start with `Nidz API`
- app portal, frontend resource loading, or CORS symptoms:
  - start with `Auth-Broker` and `Envoy`
  - then read the relevant Confluence feature doc
- TLS handshake, weak cipher, or unsupported cipher symptoms:
  - start with `Envoy`
  - then inspect `OPS` and `Terraform` for runtime config and platform-specific wiring
- logging mismatch, activity-search discrepancy, or session-versus-connection behavior:
  - start with `Auth-Broker`
  - then inspect feature docs, logging code paths, and any ops or dashboard-side handling
- deployment-wave or recent-regression symptoms:
  - start with `Release Info`
  - then inspect the likely owning repo plus `OPS` or `Terraform` if runtime config changed

## First Source Selection Rules

- If the message contains a Jira link, use Jira first.
- If the message contains a feature name or design term, use Confluence first.
- If the message contains a request ID or narrow timeframe, use Splunk early.
- If the message contains a synthetic test name, detector link, or screenshot from an external monitor, use SignalFx as corroboration after scoping the issue.
- If the symptom suggests cipher support, TLS behavior, routing, or runtime config, use ops, terraform, and release-info early.
- If the symptom is intermittent, node-specific, or worse immediately after deploy, check deployment context and node-local sync state early.
- If the message suggests a clear request-path phase, use source code only after anchoring the symptom in the architecture flow.

## What To Record In Notes

Capture these in the per-investigation artifacts:
- normalized symptom statement
- environment and timeframe
- candidate components
- first evidence sources chosen and why
- missing information that blocks stronger conclusions

Add to `ai/rca/CFD_RCA_NOTES.md` only if the investigation reveals a short reusable debugging pattern.
