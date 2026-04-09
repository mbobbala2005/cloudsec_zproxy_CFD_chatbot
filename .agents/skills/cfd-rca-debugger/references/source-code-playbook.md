# Source Code Playbook

Use this playbook when a CFD requires code-level reasoning or recent-change correlation.

## Required Inputs

- Likely owning component or request-path phase
- Environment and timeframe
- Symptom signature, error text, or failing behavior

## Repository Setup

Read `references/repo-paths.md` for required local repository paths.

Before code-level debugging:
- preferred: `./scripts/prepare_repo_context.sh`
- single-repo sync: `./scripts/sync_repos.py --repo AUTH_BROKER_REPO_PATH`
- `git -C <repo> fetch --all --prune --tags`
- `git -C <repo> pull --ff-only`

If pull cannot fast-forward, stop and ask the user how to proceed.

## Investigation Pattern

1. Start from the request-path phase, not from repo names alone.
2. Choose the most likely owning repo first.
3. Inspect the adjacent repo in the same request path if the first repo does not explain the symptom.
4. Correlate source code with:
   - architecture docs
   - Jira issue details
   - Confluence design docs
   - ops, terraform, and release context when runtime behavior may differ from code intent
   - Splunk or SignalFx evidence
5. Check recent changes only after you understand the owning code path.
6. Record exact file paths, functions, and evidence in the per-investigation artifacts, and add to `ai/rca/CFD_RCA_NOTES.md` only when the lesson is reusable.

## Component-Oriented Starting Points

### Auth-Broker

Start here for:
- login, loginvalidate, callback, or cookie behavior
- JWT generation or validation
- policy enforcement and session setup
- app portal authentication headers

Useful areas:
- `cmd/auth-broker/main.go`
- `cmd/auth-broker/auth.go`
- `cmd/auth-broker/cookie.go`
- `cmd/auth-broker/authCtx.go`
- `cmd/auth-broker/rulecache.go`
- `cmd/auth-broker/rule_watcher.go`

Useful internal verification surfaces:
- `/v1/internal/orgtorulemap`

### Envoy

Start here for:
- auth filter behavior
- upstream routing
- pass-through issues
- request-path behavior around login or loginvalidate

Useful areas:
- `src/auth_filter/auth_broker.cc`
- `src/auth_filter/auth_filter.cc`
- `src/mt_proxy/mt_proxy.cc`

### Envoy Controller

Start here for:
- xDS config
- listeners, routes, clusters, and filter chains
- websocket or guacamole-lite routing

Useful areas:
- `cmd/resource.go`

### Policy Broker And Policy Gen

Start here for:
- allow or deny mismatches
- policy evaluation
- IPS or DLP gating

Useful areas:
- `cloudsec_zproxy_policy_broker/pkg/policybroker/evaluate.go`
- `cloudsec_zproxy_policy_gen/pkg/evaluator/evaluator.go`
- `cloudsec_zproxy_policy_gen/pkg/dlpevaluator/dlpevaluator.go`

### Guacd And Guacamole-lite

Start here for:
- RDP or SSH failures
- token handling
- websocket bridge issues
- preconnection or proxy-protocol flow

Useful areas:
- `patches/freerdp/*.patch`
- `patches/guacamole-server/*.patch`
- `guacamole-lite-cisco-ztna/src/index.js`
- `guacamole-lite-cisco-ztna/src/guacamoleLite.js`
- `guacamole-lite-cisco-ztna/src/settings.js`

### Nidz API

Start here for:
- monitor or check implementation details
- how a failing monitor maps to a product path

Useful areas:
- `checks/*.sh`
- `cmd/main.go`
- `cmd/handlers.go`

### Release Info

Use this when the issue appears regression-like or rollout-specific.

Goal:
- correlate likely owning component changes with the CFD timeframe

### Ops And Terraform

Use these when the issue may be caused by:
- runtime config divergence
- cipher or TLS support
- routing or listener wiring
- platform-specific behavior that is not obvious from service code alone

## Example CFD Patterns

### Weak Cipher Or TLS Support Issue

Do not start with Splunk by default.

Start with:
- `Envoy` code
- `OPS` repo runtime config
- `Terraform` platform wiring if the issue appears environment-specific
- deployment context if the issue is newly introduced in some waves only

### Activity Search Shows A Different IP Than The Actual Connection

Treat this as a code-path and behavior-semantics problem first.

Start with:
- `Auth-Broker` logging flow and connection lifecycle
- architecture or feature docs for intended behavior
- Jira or Confluence context for the feature proposal
- then validate whether per-session versus per-connection logging explains the symptom

### Intermittent Callback 400 Or Missing Org On One Node

Treat this as a node-local auth-state problem before assuming origin or TLS.

Start with:
- `Auth-Broker` callback and session path in `auth.go` and `authCtx.go`
- `rulecache.go` and `rule_watcher.go` for org-to-rule-hash population
- `/v1/internal/orgtorulemap` on the affected node
- node-local `rules_logic.json` or synced rules presence
- `OPS` startup gating for syncer-client completion

Look for:
- callback falling back into login
- missing org `ruleHash`
- one or more nodes missing org state while others are healthy

Recent permanent-fix reference points:
- `cloudsec_zproxy_auth/cmd/auth-broker/rule_watcher.go` increased the rules-logic synapse receptor pool size from `1` to `10`
- `cloudsec_zproxy_ops/slvm/packer/ansible/roles/zproxy-auth-broker/files/service/run` waits for `/dev/shm/syncer_client_init_done` before starting auth-broker

## Evidence Rules

- Prefer direct function, handler, endpoint, or code-path matches.
- Do not infer root cause from a repo name or broad component label alone.
- Keep evidence citations concrete: file path, function, route, or commit context.
