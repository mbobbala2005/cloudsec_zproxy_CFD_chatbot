# Query Intake Playbook

Use this playbook to choose the right first source for a BAP product or architecture question.

The examples below are representative, not exhaustive.

## Goal

Turn a loosely phrased question into:
- the actual question being asked
- the likely owning component
- the best first source to inspect

## Inputs To Capture

- exact question text
- feature name, config knob, or request-path term
- whether the user is asking about support, implementation, runtime behavior, or ownership
- any environment, PR, Jira, Confluence term, or repo already named

## Question Classification

### Feature Support Or Semantics

Use this when the question is:
- do we support this
- what happens if a resource has multiple destinations
- is this behavior expected

Start with:
- `docs/architecture.md`
- `references/securitydocs_playbook.md`
- Confluence feature docs
- the likely owning repo once the feature area is identified

### Request-Path Behavior

Use this when the question is about:
- upstream or downstream handling
- proxying
- cookie validation
- federation or policy path ownership

Start with:
- `docs/architecture.md`
- `Envoy`
- `Envoy Controller`
- `Auth-Broker` when auth or session flow is involved

### Runtime Behavior

Use this when the question is about:
- accepted ciphers
- idle timeout
- listener behavior
- TLS settings
- config-dependent routing

Start with:
- source repo for the likely owning component
- `OPS`
- `Terraform`
- `Release Info` if the behavior may differ by environment or wave

### Ownership Or Repo Lookup

Use this when the question is:
- which team or repo owns this
- where is this implemented

Start with:
- `docs/repo_links.md`
- `docs/architecture.md`

### Documentation Gap

Use this when the question is:
- I do not see this in docs
- is this unsupported or just undocumented

Start with:
- current docs
- official support docs
- Confluence
- then source implementation

## First Source Selection Rules

- If the question names a feature or design term, use Confluence first.
- If the question names a repo, handler, or config file, go to source quickly.
- If the question is about ciphers, timeouts, or runtime knobs, use deployment context early.
- If the question is about request-path ownership, anchor it in `docs/architecture.md` before tracing code.
- If docs are silent, answer from implementation only after stating that the doc layer is incomplete.

## Good Mappings For Common Questions

- multiple destinations for a BAP private resource:
  - feature docs
  - resource-model implementation
  - Auth-Broker and Envoy Controller if selection or routing behavior matters
- upstream or downstream behavior in Envoy:
  - architecture flow
  - Envoy source
  - Envoy Controller xDS config path
- accepted ciphers:
  - Envoy source
  - OPS and Terraform
  - release context if the answer may differ by environment
- idle timeout:
  - Envoy timeout config
  - Auth-Broker session or cookie behavior if the question is user-session oriented
  - OPS and Terraform for deployed values
- application portal or browser-based user flow:
  - official support docs
  - architecture flow
  - Auth-Broker, Envoy, and feature docs
- policy, access, or block-page semantics:
  - architecture flow
  - Auth-Broker
  - Policy Broker or Policy Gen
- activity-search, logging, or reporting semantics:
  - feature docs
  - owning repo
  - dashboard or logging implementation only if needed
