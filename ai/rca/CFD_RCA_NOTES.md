# CFD RCA Notes

This file is a compact reusable knowledge base for future CFD debugging.

Use it like lightweight pattern memory:
- scan it early for similar failure shapes
- treat it as hypothesis acceleration, not proof
- append only short evidence-backed lessons
- keep entries searchable and merge duplicates

Recommended entry shape:
- `date | pattern`
- `Signals:` 1 short line
- `Reuse:` 1 short line

## Notes

### 2026-04-09 | Auth-broker rules sync gap can surface as FedGW 400 after SSO

Signals: `/v1/logincallback` returns `303` back to `/v2/gw/auth/begin`, FedGW request URL becomes very large, and the failing node is missing the org in auth-broker and syncer `rules_logic` state.

Reuse: Check node-local rules state and Splunk missing-org rule-logic errors by host before assuming origin or TLS issues; restart of auth-broker can force a full sync, and permanent fixes were startup gating on sync completion plus higher rules-logic processing concurrency.
