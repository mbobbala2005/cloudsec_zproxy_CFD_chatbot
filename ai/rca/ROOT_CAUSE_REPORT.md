# ZTBAP-649 Root Cause Report

## Executive Summary

`ZTBAP-649` is not primarily an origin-app `400` and is not supported as a TLS-handshake defect from current evidence. The visible failure is a Cisco Federation Gateway `400` caused by an oversized `/v2/gw/auth/begin/?v=...` URL. The deeper product-side issue is that Auth-Broker is redirecting the browser back into login from the `/v1/logincallback` path instead of completing session creation. The most likely trigger for that callback fallback is a missing org `ruleHash` in Auth-Broker's in-memory rule cache.

## Confirmed Evidence

- Jira summary and description describe intermittent browser-based BAP failures after SSO for `Dealer Access Portal`.
- Screenshot evidence shows the BAP transaction is `Allowed`, which supports that policy path evaluation is not the user-visible failure.
- HAR evidence shows the final `400` is returned by `fg.id.sse.cisco.com`.
- HAR evidence shows `/v1/logincallback` itself returns a `303` back to FedGW.
- HAR evidence shows no successful session-establishment behavior on callback before the browser is sent back to FedGW.
- The second FedGW URL expands to about `17.4 KB` in one HAR and `20.8 KB` in the other.

## Code-Based Explanation

1. Envoy routes callback requests to Auth-Broker `/v1/logincallback`.
   - Source: [auth_broker.cc](/Users/mbobbala/cisco/cloudsec_zproxy_envoy_zproxy/src/auth_filter/auth_broker.cc#L44)

2. `loginCallbackHandler()` parses the FedGW token and then calls `authorizeAndCreateSession()`.
   - Source: [auth.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/auth.go#L405)

3. If `authorizeAndCreateSession()` cannot complete the allow path, it falls back to `loginRedirect(w, r)`.
   - Source: [authCtx.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/authCtx.go#L596)

4. `loginRedirect` is the normal `loginHandler()`.
   - Source: [auth.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/auth.go#L74)

5. `handleAllowCase()` explicitly returns `false` when `getRuleHashOfOrg(authCtx.app.OrgID)` fails.
   - Source: [authCtx.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/authCtx.go#L510)

6. `getRuleHashOfOrg()` reads a process-local in-memory map, not a durable shared cache.
   - Source: [rulecache.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/rulecache.go#L111)

7. That map is filled by a watcher callback on rules-logic file events.
   - Source: [rule_watcher.go](/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/rule_watcher.go#L65)

## Root Cause

The most likely root cause is an Auth-Broker defect path where callback session creation depends on an org `ruleHash` that is missing from the local in-memory cache on the serving auth-broker instance. When that lookup fails, the callback path falls back to `loginHandler()`, which re-encodes the already-large callback URL into a new FedGW login request. That recursive growth pushes the FedGW `v=` request beyond acceptable length, and the gateway returns `400 Bad Request`.

Post-incident node verification strengthened that explanation:
- on the problematic node, both the auth-broker org `ruleHash` state and the expected `rules_logic.json` org content were missing
- restarting auth-broker on that node caused a full sync / repopulation path and resolved the issue

## Customer-Specific Amplifier

The customer's app upgrade likely increased the size of the original post-SSO URL or related state. That appears to be why this callback-loop defect now surfaces as a visible `400` instead of a smaller redirect anomaly. The HARs show first-pass callback URLs already in the multi-kilobyte range, which makes the second nested FedGW redirect large enough to fail.

This is a supported inference, not a directly decoded origin URL comparison.

## Why The Failure Appears Intermittent

Intermittency is consistent with the implementation because the `ruleHash` is stored in a process-local map populated by watcher events. If only some auth-broker instances have missing or stale population for this org, requests can succeed or fail depending on which instance handles the callback.

This is an inference from the code structure. Runtime logs would be needed to prove the exact instance-level miss pattern.

That inference is now consistent with the operational check performed during incident handling: the issue was isolated to a problematic node whose local rules state was incomplete.

## What Is Not Supported By Current Evidence

- The customer origin app directly returning the `400`
- TLS `1.3` as the primary failure mechanism
- A pure BAP policy block

## Confidence

- High confidence:
  - callback re-login loop is happening
  - oversized FedGW URL is the immediate reason for the visible `400`
- Medium-high confidence:
  - missing `ruleHash` is the callback fallback trigger
- Medium confidence:
  - intermittent behavior is due to instance-local cache population differences

## Best Verification Steps

- Check auth-broker logs on the failing timeframe for:
  - `unable to find ruleHash for orgId 8276995`
  - repeated callback-to-login redirects for the same request chain
- Verify whether all auth-broker instances have the org's rules-logic file loaded and hashed
- Reproduce with the same callback flow while capturing auth-broker logs and request IDs

## Permanent Fixes Landed

- `cloudsec_zproxy_ops` PR `#2293`
  - auth-broker service startup now waits for `/dev/shm/syncer_client_init_done` before starting
- `cloudsec_zproxy_auth` PR `#102`
  - rules-logic synapse receptor pool size increased from `1` to `10` for faster event processing
