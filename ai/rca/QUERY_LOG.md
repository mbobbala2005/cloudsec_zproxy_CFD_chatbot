# Query Log For ZTBAP-649

## Constraints

- Jira comments were not fetched.
- Ticket data was fetched from Jira using field-restricted issue API calls only.

## Inputs Used

- Issue key: `ZTBAP-649`
- Jira description and attachments
- User direction: provide RCA, do not fetch Jira comments

## Jira Retrieval Performed

1. Loaded Jira and Confluence credentials into local `.env`.
2. Fetched Jira issue without comments using:
   - `GET /rest/api/3/issue/ZTBAP-649?fields=summary,description,attachment,labels,environment,status,priority,issuetype,created,updated`
3. Downloaded Jira attachments referenced in the issue:
   - `ai/rca/artifacts/ztbap-649-honda-1.har`
   - `ai/rca/artifacts/ztbap-649-honda-2.har`
   - `ai/rca/artifacts/ztbap-649-screenshot.png`
4. Viewed the screenshot locally.

## Local Evidence Queries

1. Read RCA workflow references:
   - `.agents/skills/cfd-rca-debugger/SKILL.md`
   - `ai/rca_system_prompt.md`
   - `.agents/skills/cfd-rca-debugger/references/jira-playbook.md`

2. Parsed HAR files for:
   - redirect chains
   - `Location` headers
   - `Set-Cookie` headers
   - final failing URL and status

3. Measured failing FedGW request sizes from HAR.

4. Inspected Auth-Broker callback and login code:
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/auth.go`
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/authCtx.go`
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/authCtx.go`

5. Inspected Envoy auth-subrequest generation:
   - `/Users/mbobbala/cisco/cloudsec_zproxy_envoy_zproxy/src/auth_filter/auth_broker.cc`

6. Inspected rule-hash cache implementation:
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/rulecache.go`
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/rule_watcher.go`
   - `/Users/mbobbala/cisco/cloudsec_zproxy_auth/cmd/auth-broker/posture.go`

7. Checked local git history for likely relevant code paths:
   - `git log` and `git blame` on `authCtx.go`, `rulecache.go`, and `rule_watcher.go`

## Key Results From Queries

- Jira description confirms:
  - intermittent `400` after SSO
  - customer app upgrade
  - reported TLS upgrade
  - client-based / RA-VPN flows working

- HAR confirms:
  - final `400` is from `fg.id.sse.cisco.com`
  - `/v1/logincallback` is already redirecting back to FedGW
  - callback response does not establish a usable session cookie
  - failing FedGW URL lengths are about `17.4 KB` and `20.8 KB`

- Code confirms:
  - callback handler calls `authorizeAndCreateSession()`
  - callback can fall back to `loginRedirect()`
  - `loginRedirect()` is `loginHandler()`
  - `handleAllowCase()` returns `false` when `getRuleHashOfOrg()` fails
  - `ruleHash` is kept in process-local in-memory cache populated by watcher events

## Outcome Of Investigation

- Confirmed customer-visible symptom mechanism:
  - callback-to-login loop causes oversized FedGW redirect URL, then FedGW returns `400`
- Best-supported product-side trigger:
  - `ruleHash` cache miss during callback session creation
- Remaining uncertainty:
  - exact operational reason the `ruleHash` is intermittently unavailable on affected auth-broker instance(s)
