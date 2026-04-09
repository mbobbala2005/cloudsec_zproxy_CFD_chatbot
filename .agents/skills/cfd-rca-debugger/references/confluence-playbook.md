# Confluence Playbook

This playbook documents how to access Confluence content for BAP architecture and CFD RCA agents.

## Purpose

Use this playbook when an agent needs to:
- fetch a known Confluence page by page ID
- search Confluence for product documents
- extract page title, space, web link, and body content

This is the preferred pattern for Confluence Cloud access in this repo.

## Authentication

For the Cisco Atlassian Cloud instance, the working access pattern was:
- Confluence Cloud REST API
- Basic auth with `email + API token`

The direct browser page URL with bearer-token auth redirected to login, but the REST API with standard Confluence Cloud auth succeeded.

## Required Environment Variables

```bash
export CONFLUENCE_BASE_URL="https://cisco-sbg.atlassian.net/wiki"
export CONFLUENCE_USER="<your-cisco-email>"
export CONFLUENCE_API_TOKEN="<your-atlassian-api-token>"
```

## Core Endpoints

Fetch a page by content ID:

```text
GET /wiki/rest/api/content/{page_id}?expand=title,space,body.storage
```

Search with CQL:

```text
GET /wiki/rest/api/search?cql=<CQL>&limit=<N>
```

Useful fields in the response:
- `title`
- `space.key`
- `body.storage.value`
- `_links.webui`

## Example 1: Fetch A Known Page

This is the working example used to access the App Portal document.

Page:
- Title: `App Portal`
- Page ID: `1294165774`
- Web URL: `https://cisco-sbg.atlassian.net/wiki/spaces/PROD/pages/1294165774/App+Portal`

Command:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -H "Accept: application/json" \
  "$CONFLUENCE_BASE_URL/rest/api/content/1294165774?expand=title,space,body.storage"
```

Compact extraction example:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -H "Accept: application/json" \
  "$CONFLUENCE_BASE_URL/rest/api/content/1294165774?expand=title,space,body.storage" \
| jq -r '[.title, .space.key, ._links.webui] | @tsv'
```

Expected shape:
- title: `App Portal`
- space: `PROD`
- web path: `/spaces/PROD/pages/1294165774/App+Portal`

## Example 2: Search For BAP CORS Documents

This is the working search pattern used on April 8, 2026 to look for BAP CORS material.

Broad text search:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -G "$CONFLUENCE_BASE_URL/rest/api/search" \
  --data-urlencode 'cql=text~"CORS" and text~"BAP"' \
  --data-urlencode 'limit=10' \
  -H "Accept: application/json"
```

Targeted site search:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -G "$CONFLUENCE_BASE_URL/rest/api/search" \
  --data-urlencode 'cql=siteSearch~"BAP CORS"' \
  --data-urlencode 'limit=10' \
  -H "Accept: application/json"
```

Compact extraction example:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -G "$CONFLUENCE_BASE_URL/rest/api/search" \
  --data-urlencode 'cql=siteSearch~"BAP CORS"' \
  --data-urlencode 'limit=10' \
  -H "Accept: application/json" \
| jq -r '.results[]? | [.content.title, (.url // .content._links.webui // "")] | @tsv'
```

Relevant search hits found:
- `CORS enablement in BAP` in space `ZTAPROXY`
- `CORS support for BAP` in space `PROD`

Direct links:
- `https://cisco-sbg.atlassian.net/wiki/spaces/ZTAPROXY/pages/1385911643/CORS+enablement+in+BAP`
- `https://cisco-sbg.atlassian.net/wiki/spaces/PROD/pages/1294306070/CORS+support+for+BAP`

## Extracting A Quick Text Preview

Confluence page bodies come back as HTML in `body.storage.value`.

Quick preview command:

```bash
curl -sS \
  -u "$CONFLUENCE_USER:$CONFLUENCE_API_TOKEN" \
  -H "Accept: application/json" \
  "$CONFLUENCE_BASE_URL/rest/api/content/1294306070?expand=title,space,body.storage" \
| jq -r '.body.storage.value' \
| sed 's/<[^>]*>/ /g' \
| tr -s ' ' \
| cut -c1-700
```

This is enough to quickly inspect the first chunk of a page before doing deeper parsing.

## Recommended Retrieval Workflow

For agent retrieval:
1. If the page ID is known, fetch the page directly.
2. If only a topic is known, search with CQL first.
3. Return the page title, space, and web link with the answer.
4. Use the body content for summarization, not as raw output.
5. Keep tokens in environment variables only.