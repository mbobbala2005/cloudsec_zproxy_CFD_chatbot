# Deployment Context Playbook

Use this playbook when a CFD may depend on runtime configuration, platform wiring, latest promotions, or deployment-wave timing.

## Primary Repos

- `OPS_REPO_PATH`
- `TERRAFORM_REPO_PATH`
- `RELEASE_INFO_REPO_PATH`

## When To Use Each Repo

### OPS

Use `OPS` when the issue may depend on:
- runtime config rendered onto nodes
- service startup configuration
- startup ordering relative to syncer-client or other init gates
- cipher or TLS knobs
- proxy or sidecar configuration
- environment-specific operational wiring

### Terraform

Use `Terraform` when the issue may depend on:
- platform-specific networking
- security groups
- listener or routing infrastructure
- synthetic or detector deployment
- environment-specific infrastructure behavior

### Release Info

Use `Release Info` when the issue may depend on:
- latest deployment wave
- promotion timing
- environment family
- whether a change landed in some DCs but not others

## RCA Workflow

1. Decide whether the symptom looks like:
   - application logic
   - runtime config
   - infrastructure wiring
   - deployment regression
2. If runtime config may matter, inspect `OPS` before assuming the application repo is wrong.
3. If the symptom is node-specific or post-deploy, compare startup gating and node-local synced state before assuming a code-path bug.
   - Check whether auth-broker started only after sync completion.
   - Check whether the affected node has the expected local `rules_logic` data and auth-broker org-to-rule map entries.
4. If infrastructure wiring may matter, inspect `Terraform`.
5. If the issue might be recent or wave-specific, inspect `Release Info` before drawing conclusions from one environment.
6. Correlate findings back to:
   - architecture docs
   - source repo behavior
   - Splunk or SignalFx evidence

## Good Triggers For This Playbook

- weak cipher or unsupported TLS handshake
- routing works in one environment but not another
- issue started after a rollout
- issue only happens in some DCs or waves
- runtime behavior does not match source-code expectations
- one node is missing an org in `rules_logic` or the auth-broker org-to-rule map
- auth callback or cookie behavior fails only on some nodes after deploy

## Evidence Recording

Capture in the per-investigation artifacts:
- which repo was checked
- what config, deployment, or wave fact mattered
- how that fact supports or rejects a hypothesis

Add to `ai/rca/CFD_RCA_NOTES.md` only if the deployment finding is a short reusable debugging pattern.

## Reusable BAP Pattern

For intermittent auth-broker callback or cookie issues after deploy:
- verify whether the affected node is missing the org in both node-local `rules_logic` data and auth-broker's org-to-rule map
- verify whether auth-broker startup waited for syncer-client completion
- if a restart after sync completion restores the missing org state, record that as confirmation of a node-local sync or watcher population problem
- keep the permanent fix separate from the temporary recovery

Known permanent-fix locations:
- `cloudsec_zproxy_ops/slvm/packer/ansible/roles/zproxy-auth-broker/files/service/run`
- `cloudsec_zproxy_auth/cmd/auth-broker/rule_watcher.go`
