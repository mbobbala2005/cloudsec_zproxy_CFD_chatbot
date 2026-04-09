# Runtime Behavior Playbook

Use this playbook for BAP questions whose answer depends on deployed configuration rather than product docs alone.

The use cases below are representative, not exhaustive.

## Use Cases

- accepted cipher suites
- TLS versions or handshake settings
- idle timeout
- listener or route timeout values
- websocket or long-lived connection behavior
- environment-specific differences in routing or security posture
- auth-broker startup ordering or sync-completeness questions
- node-local org-to-rule map or rules-logic state

## Primary Sources

- source repo for the owning component
- `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`
- `OPS`
- `Terraform`
- `Release Info`

## Investigation Pattern

1. Identify the owning layer first.
   - `Envoy` for proxy-layer TLS and timeout behavior
   - `Auth-Broker` for session, cookie, callback, or rule-hash semantics
   - `Envoy Controller` when the value is pushed through xDS or generated config
2. Find the implementation default.
3. Find the deployed or rendered config.
4. Check whether the answer may vary by environment, platform, or rollout wave.
5. Only then give a definitive answer.

For auth-broker runtime-state questions:
- verify node-local sync completion in `OPS`
- verify auth-broker rule-hash state, not just source defaults
- do not assume one healthy node means the fleet is healthy

## Answer Rules

- If the value is globally fixed, say so and cite where it is defined.
- If the value is configurable, say which layer controls it.
- If the value can vary by environment, do not answer with a single number unless you verified the target environment.
- If the state can vary by node, do not answer from one host unless you verified the fleet behavior or the target host.
- If the question mixes session timeout and proxy timeout, separate those concepts clearly.

## Common Traps

- answering from source defaults when OPS overrides them
- answering from docs when runtime config changed later
- treating session expiry and network idle timeout as the same thing
- assuming one environment represents all environments
