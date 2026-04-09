# SignalFx Synthetics Playbook

Use this when a customer-facing issue can be corroborated with Splunk Observability or SignalFx synthetic tests.

## Safety Rules
- Keep token/secret in environment variables only.
- Do not commit tokens, signed screenshot URLs, or raw payloads with sensitive fields.
- Screenshot/result links can be time-limited pre-signed URLs; treat them as ephemeral.

## Required Environment Variables
- `SIGNALFX_BASE_URL`
- `SIGNALFX_API_TOKEN`

## Auth Notes (Validated In This Repo Session)
- For this org, `X-SF-TOKEN` expects the API token value (often what teams call "secret"), not token ID.
- Token ID alone may return `401`.
- Base API host used successfully: `https://api.us0.signalfx.com`.
- Org host can also work: `https://cisco-opendnsbu-sse.signalfx.com`.
- `GET /v2/synthetics/tests/{id}` may return `404` for some tests even when token is valid; use `/v2/synthetics/tests/{id}/runs` as the primary existence/access check.

## Core APIs

### 1) List tests
```bash
curl -sS "${SIGNALFX_BASE_URL}/v2/synthetics/tests?page=1&per_page=50" \
  -H "X-SF-TOKEN: $SIGNALFX_API_TOKEN"
```

### 2) Filter BAP tests
`customProperties` is an array of key/value pairs, not an object.
```bash
jq -r '
  .tests[]
  | select(any(.customProperties[]?;
      ((.key // "") | ascii_downcase) == "product"
      and ((.value // "") | ascii_downcase) == "bap"))
  | [.id, .type, .active, .name] | @tsv
'
```

### 3) Recent runs for one test
```bash
curl -sS "${SIGNALFX_BASE_URL}/v2/synthetics/tests/${TEST_ID}/runs?limit=10" \
  -H "X-SF-TOKEN: $SIGNALFX_API_TOKEN"
```

### 4) Run-level failure reason
```bash
curl -sS "${SIGNALFX_BASE_URL}/v2/synthetics/runs/${RUN_ID}" \
  -H "X-SF-TOKEN: $SIGNALFX_API_TOKEN"
```
Important fields:
- `run.id`
- `run.status`
- `run.message` (often includes failing step and error)
- `run.artifactsTimestampMs`
- `run.locationId`, `run.testId`, `run.timestamp`

### 5) Find run IDs in the relevant issue window
When you know the approximate timeframe, first locate run IDs from test runs, then fetch run details.
```bash
TEST_ID="<synthetics_test_id>"
WINDOW_START="<issue_start_minus_10m_utc>"   # e.g. 2026-03-07T09:08:57.000Z
WINDOW_END="<issue_end_plus_10m_utc>"        # e.g. 2026-03-07T09:38:57.000Z
PAGE=1
PER_PAGE=100

# Iterate page-wise until you hit the relevant issue time window.
curl -sS "${SIGNALFX_BASE_URL}/v2/synthetics/tests/${TEST_ID}/runs?page=${PAGE}&per_page=${PER_PAGE}" \
  -H "X-SF-TOKEN: $SIGNALFX_API_TOKEN" \
| jq -r --arg s "$WINDOW_START" --arg e "$WINDOW_END" '
    .runs[]
    | select(.timestamp >= $s and .timestamp <= $e)
    | [.timestamp, .runId, .success, .runDurationMs, .locationId]
    | @tsv
  '
```

## Screenshot / Failed Result Access

### Preferred path
- Use the synthetic run detail API first.
- If the engineer or ticket already contains result URLs or screenshots, use them as supporting evidence.
- Treat screenshot or result URLs as ephemeral because they may be pre-signed and time-limited.

### API limitation note
- In this environment, direct artifact endpoints under `/v2/synthetics/runs/{run_id}/artifacts` returned `404`.
- Endpoints `/v2/synthetics/runs/{run_id}/result` and `/steps` also returned `404`.
- Older run IDs may return `404 {"code":"not_found"}` on `/v2/synthetics/runs/{run_id}` (likely retention/backfill limit), even though run entries still appear in paged test run history.
- Use run-level message plus any result URL or screenshot already shared by the engineer as fallback.

## Practical Triage Flow
1. Identify the relevant synthetic test name or ID for the same user-facing path.
2. Pull latest runs and confirm if failure is persistent vs transient.
3. Pull run-level `message` to identify failing step.
4. If a result URL or screenshot was already shared by the engineer, use it as supporting evidence.
5. Correlate with BAP logs:
   - If no app-hostname hits in BAP logs during failure window, suspect pre-BAP path (DNS/network/TLS/front-door).
   - If hits exist with errors, investigate auth/envoy/app behavior.
6. Treat synthetic evidence as corroboration of the customer issue, not as root cause by itself.
