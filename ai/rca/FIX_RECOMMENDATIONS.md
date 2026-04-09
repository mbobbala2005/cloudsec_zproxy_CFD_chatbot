# ZTBAP-649 Fix Recommendations

## Immediate Engineering Direction

1. Treat this as an Auth-Broker callback/session defect, not as a customer-origin `400`.

2. Validate the suspected trigger in runtime logs:
   - search for `unable to find ruleHash for orgId 8276995`
   - correlate to callback requests and repeated FedGW redirects

3. Check auth-broker fleet consistency:
   - confirm all serving instances have the org's rules-logic data loaded
   - confirm watcher init-scan and subsequent update events populated `orgRuleMap`
   - compare affected versus healthy nodes before assuming a fleet-wide logic bug

## Product Fix Direction

1. Do not redirect from callback back to `loginHandler()` on `ruleHash` lookup failure.
   - safer behaviors would be:
     - explicit error page
     - retryable internal rehydrate of rule hash
     - controlled failure path that does not re-wrap callback URLs

2. Decouple callback session creation from a fragile process-local cache dependency where possible.

3. Add guardrails on callback re-login behavior:
   - detect when the incoming request is already `/v1/logincallback`
   - block recursive login redirection from callback
   - emit a clear error instead of generating a larger FedGW URL

4. Add URL-size protection before redirecting to FedGW.
   - if the generated FedGW URL exceeds a safe threshold, fail explicitly and log root context instead of sending an oversized request

## Operational Mitigation Ideas

1. Refresh or restart affected auth-broker instances only if logs confirm missing org rule-hash state on a subset of pods.
   - in this incident, restarting auth-broker on the affected node restored sync-derived state and cleared impact

2. Verify rule-sync and watcher health for org `8276995`.

3. If customer impact is urgent, check whether a shorter post-SSO landing path can temporarily reduce callback URL size while the callback-loop defect is addressed.
   - This would be mitigation, not the real fix.

## Additional Notes

- The reported TLS `1.3` change should stay secondary until direct evidence supports it.
- The customer app upgrade still matters because it likely increased URL/state size enough to expose the callback-loop defect as a hard `400`.

## Permanent Fixes Merged

- `cloudsec_zproxy_ops` PR `#2293`
  - auth-broker run script waits for syncer-client initialization to complete before startup
- `cloudsec_zproxy_auth` PR `#102`
  - rules-logic watcher receptor pool increased from `1` to `10`
