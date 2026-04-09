# Splunk Playbook

## Safety Rules
- Use read-only access for investigations.
- Do not embed credentials in files or commands.
- Redact PII/secrets in notes and tickets.

## Required Environment Variables
- `SPLUNK_BASE_URL`
- `SPLUNK_TOKEN`
- `SPLUNK_APP`
- `SPLUNK_DEFAULT_INDEX`

## API Access Pattern
- Validate token/context:
  - `GET $SPLUNK_BASE_URL:8089/services/authentication/current-context?output_mode=json`
  - Header: `Authorization: Bearer $SPLUNK_TOKEN`
- Run search via management API (`services/search/jobs`) using `exec_mode=oneshot`.
- Prefer `oneshot` for RCA pulls to avoid preview/duplication artifacts.

## Query Pattern
1. Start with tight absolute time bounds: earliest should be at most 10 minutes before the first reported symptom or reproduction time.
2. Filter by service, environment, and correlation/request ID.
3. Group by signature to identify top offenders.
4. Drill into representative events.
5. Expand time window only when needed to validate hypothesis; record expansion reason in `ai/rca/QUERY_LOG.md`.
6. For intermittent or node-specific incidents, always break down by `host` before concluding the defect is global.

## Time-Bound Gotcha (Important)
- For API searches, pass time bounds as request params (`earliest_time`, `latest_time`) instead of embedding `earliest=` / `latest=` in the SPL string.
- Keep SPL focused on filters; keep time bounds outside SPL for consistent behavior.
- Use absolute UTC (RFC3339, `YYYY-MM-DDTHH:MM:SSZ`) when correlating with the first reported symptom, reproduction time, or other evidence sources.

## Example API Query (Auth Broker, Last 10m)
```bash
curl -sS -k "$SPLUNK_BASE_URL:8089/services/search/jobs" \
  -H "Authorization: Bearer $SPLUNK_TOKEN" \
  --data-urlencode "search=search index=$SPLUNK_DEFAULT_INDEX sourcetype=zproxy-auth-broker | sort - _time | head 100" \
  --data-urlencode "earliest_time=-10m" \
  --data-urlencode "latest_time=now" \
  --data-urlencode "exec_mode=oneshot" \
  --data-urlencode "output_mode=json"
```

## Example SPL Templates
```spl
search index=$SPLUNK_DEFAULT_INDEX sourcetype=zproxy-auth-broker
| eval parsed=if(match(_raw, "^\\{"), spath(_raw, "message"), null())
| stats count by host source sourcetype
```

```spl
search index=$SPLUNK_DEFAULT_INDEX sourcetype=zproxy-auth-broker "unable to find ruleHash for orgId"
| stats count by host
```

```spl
search index=$SPLUNK_DEFAULT_INDEX sourcetype=zproxy-auth-broker ("unable to find ruleHash for orgId" OR "/v1/logincallback" OR "loginCallbackHandler")
| stats count by host
```

- Use the first query when you suspect missing org-to-rule-hash state on a subset of auth-broker nodes.
- Use the second query when you need to correlate callback-path failures with host-level concentration.

## API Debug Pattern (When Results Are Empty)
```bash
resp=$(curl -sS -k "$SPLUNK_BASE_URL:8089/services/search/jobs" \
  -H "Authorization: Bearer $SPLUNK_TOKEN" \
  --data-urlencode "search=search index=$SPLUNK_DEFAULT_INDEX sourcetype=consul-agent | head 10" \
  --data-urlencode "earliest_time=2025-12-11T20:03:12Z" \
  --data-urlencode "latest_time=2025-12-11T20:15:13Z" \
  --data-urlencode "exec_mode=oneshot" \
  --data-urlencode "output_mode=json")

echo "$resp" | jq -r '.messages[]? | "\(.type): \(.text)"'
echo "$resp" | jq -r '.results[]?'
```
- If `.results` is empty, always inspect `.messages` before assuming source outage.

## Evidence Recording
For each query executed, capture:
- Why the query was run.
- Exact query text.
- Time range.
- Observed result and interpretation.
