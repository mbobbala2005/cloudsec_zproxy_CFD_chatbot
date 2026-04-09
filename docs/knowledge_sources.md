# Knowledge Sources And Access Patterns

This agent workspace is designed to use product and issue-specific context first, then use observability tools as supporting evidence.

## Source Hierarchy

Use sources in this order:
1. local product docs in this repo
2. official Cisco Secure Access support docs for documented behavior and user-facing options
3. canonical GitHub repositories
4. Confluence and Jira when connected
5. Splunk and SignalFx for verification hints and RCA evidence

## Cisco Secure Access Support Docs

Use Cisco Security Help Center pages to answer:
- whether a BAP-related behavior is officially documented
- which user-facing options exist in the Secure Access subscription
- documented limitations, ranges, prerequisites, and workflow steps
- official terminology for browser-based zero trust access, private resources, application portal, and timeout behavior

Guardrails:
- this site covers many Secure Access sub-products, so stay scoped to BAP-relevant pages only
- treat support docs as the official user-documentation layer, not as proof of internal implementation details
- if support docs and implementation appear to differ, call out the difference explicitly

Primary reference:
- `.agents/skills/bap-query-resolver/references/securitydocs_playbook.md`

## GitHub

Use GitHub to answer:
- which repo owns a component
- where a feature likely lives
- which service should be inspected for implementation detail
- where to find README or design docs in code repos

Recommended access model:
- GitHub App authentication for automation
- repo links curated in `docs/repo_links.md`
- `scripts/github_auth.py` for GitHub App backed `git` and `gh` access
- `scripts/sync_repos.py` or `scripts/prepare_repo_context.sh` before repo-backed analysis

Starter environment variables:
- `APP_ID`
- `PRIVATE_KEY_PATH`
- `INSTALLATION_ID`
- `GITHUB_BASE_URL`
- `GITHUB_API`

## Ops, Terraform, And Release Context

Use these repos when the CFD may depend on:
- runtime configuration
- cipher or TLS support
- platform-specific routing or listener behavior
- deployment wave or latest promotion timing

Canonical repos:
- `docs/repo_links.md`

Primary references:
- `.agents/skills/cfd-rca-debugger/references/repo-paths.md`
- `.agents/skills/cfd-rca-debugger/references/deployment-context-playbook.md`

## Splunk

Use Splunk to support product understanding, for example:
- identify the log source for a component
- confirm field names and log vocabulary
- point engineers to the right place for verification
- explain which service emits the relevant log family

Guardrails:
- do not default to log diving for every CFD
- do not present a live log read as a full RCA
- treat Splunk as one evidence source among docs, code, ops, and deployment context

Starter environment variables:
- `SPLUNK_BASE_URL`
- `SPLUNK_TOKEN`
- `SPLUNK_APP`
- `SPLUNK_DEFAULT_INDEX`

## SignalFx

Use SignalFx to support:
- dashboard lookup by component
- service health and traffic visualization
- metric family discovery
- topology context for how a component is observed in production

Guardrails:
- do not substitute dashboards for architecture docs or source tracing
- use SignalFx to corroborate a user-facing issue when a matching signal exists
- do not assume a synthetic or detector exists for every CFD

Starter environment variables:
- `SIGNALFX_BASE_URL`
- `SIGNALFX_API_TOKEN`

## Confluence

Confluence should become the preferred source for:
- detailed architecture explanations
- sequence diagrams
- feature decisions
- internal FAQs

API access and retrieval examples:
- `.agents/skills/cfd-rca-debugger/references/confluence-playbook.md`

Starter environment variables:
- `CONFLUENCE_BASE_URL`
- `CONFLUENCE_USER`
- `CONFLUENCE_API_TOKEN`
- `CONFLUENCE_SPACE_KEYS`

## Jira

Use Jira to support:
- issue intake when a CFD is reported as a ticket
- extracting error text, reproduction details, and environment notes
- reading comments, screenshots, and attachments
- using linked issue history as RCA context

Starter environment variables:
- `JIRA_BASE_URL`
- `JIRA_USER`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEYS`

## Answering Strategy

For most architecture or RCA tasks, the agent should:
1. identify the owning component or request-path phase
2. choose the best first evidence source
3. use logs or monitors only when they add signal
4. pull ops, terraform, and deployment context when runtime behavior may explain the issue
5. call out missing Confluence or Jira context when needed

## What Good Looks Like

Good:
- "This behavior usually belongs to Auth-Broker. Use the Auth-Broker repo for implementation detail and the login flow in `docs/architecture.md` for the high-level explanation."

Not good:
- "Check these five dashboards, then grep logs, then compare deploys."

That second style belongs to a log-first outage workflow, not CFD debugging.
