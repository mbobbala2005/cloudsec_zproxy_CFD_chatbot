# RCA Artifacts

Use this directory for RCA outputs during CFD debugging.

Recommended artifact names:
- `CFD_RCA_NOTES.md`: persistent compact knowledge base for reusable RCA patterns
- `QUERY_LOG.md`: exact Splunk, Jira, Confluence, or other queries used for the current investigation
- `ROOT_CAUSE_REPORT.md`: concise final RCA for the current investigation
- `FIX_RECOMMENDATIONS.md`: engineering follow-up and validation steps for the current investigation

Rules for `CFD_RCA_NOTES.md`:
- keep entries short and searchable
- add only new durable lessons that are likely to help future debugging
- do not dump full case narratives, raw logs, or customer-specific detail into it
- merge or tighten entries when the same pattern appears again

The per-investigation files should stay evidence-focused and avoid operational mitigation guidance unless the user explicitly requests it.
