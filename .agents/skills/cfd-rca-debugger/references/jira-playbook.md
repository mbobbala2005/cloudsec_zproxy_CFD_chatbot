# Jira Playbook

Use this playbook when a CFD is reported or discussed in Jira.

## Safety Rules

- Use read-only access for investigations.
- Keep tokens in environment variables only.
- Do not commit ticket payloads, screenshots, or attachments with sensitive data.

## Required Environment Variables

- `JIRA_BASE_URL`
- `JIRA_USER`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEYS`

## API Access Pattern

For Atlassian Cloud, use basic auth with `email + API token`.

Base endpoint style:
- `GET $JIRA_BASE_URL/rest/api/3/issue/{ISSUE_KEY}`
- `GET $JIRA_BASE_URL/rest/api/3/search/jql`

## Fetch A Known Issue

```bash
curl -sS \
  -u "$JIRA_USER:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue/$ISSUE_KEY?fields=summary,description,comment,attachment,labels,environment,status,priority,issuetype,created,updated"
```

## Search For Related Issues

```bash
curl -sS \
  -u "$JIRA_USER:$JIRA_API_TOKEN" \
  -G "$JIRA_BASE_URL/rest/api/3/search/jql" \
  --data-urlencode 'jql=project in (ZPROXY, CSECF) AND text ~ "App Portal" ORDER BY updated DESC' \
  --data-urlencode 'maxResults=10' \
  -H "Accept: application/json"
```

## Attachments

Useful fields:
- `fields.attachment[].id`
- `fields.attachment[].filename`
- `fields.attachment[].mimeType`
- `fields.attachment[].content`

If attachment content URLs are available, use the provided attachment content link with the same Jira auth context.

## RCA Workflow

1. Pull the issue description first.
2. Extract:
   - exact error text
   - reproduction steps
   - environment
   - screenshots or stack traces
   - linked feature docs or rollout notes
   - comments that narrow timeframe or blast radius
3. Treat Jira evidence as the first issue-specific source before broad log searches.
4. Use Jira text to build search terms for:
   - Confluence
   - GitHub
   - Ops and Terraform
   - Splunk
5. Record issue key, relevant comments, and attachments used in the per-investigation artifacts, and add to `ai/rca/CFD_RCA_NOTES.md` only if the ticket taught a reusable debugging pattern.

## Evidence Recording

For each Jira issue used, capture:
- issue key
- why it was relevant
- which comments or attachments influenced the RCA
- any uncertainty caused by missing or contradictory ticket details
