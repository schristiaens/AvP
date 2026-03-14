# FetchFindings — Pull Findings from Scanner

Fetch-only mode for reconnaissance. Pull findings and present them without taking action.

## Triggers

- "fetch findings"
- "scan"
- "what's vulnerable"

## Input

- Repo path (current working directory or explicit)
- Scanner source: `snyk` (default), or path to a generic normalized report file

## Steps

1. **Determine scanner source**
   - If `SNYK_TOKEN` is set and user specifies Snyk (or default): use Snyk adapter
   - If user provides a file path: use generic adapter (JSON/CSV/SARIF import)
   - Ask the human for `org_id` and `project_id` if not provided

2. **Fetch findings**
   ```bash
   uv run vuln-remediation fetch <org-id> <project-id> --severity high,critical --output table
   ```

3. **Display summary**
   - Total findings count
   - Breakdown by severity (critical / high / medium / low)
   - Breakdown by ecosystem (npm / maven / docker)
   - Breakdown by dependency type (direct / transitive / base_image)

4. **Offer next steps**
   - "Would you like to triage these findings?" → TriageFindings workflow
   - "Would you like to analyze a specific finding?" → SelectStrategy workflow
   - "Would you like the full JSON output?" → re-run with `--output json`

## Output Formats

- **Table** (default): Rich terminal table with severity coloring
- **JSON**: Full Finding model array, suitable for piping to other tools

## Notes

- This workflow does NOT modify the repository
- Findings are normalized to the `Finding` model regardless of scanner source
- Severity filter defaults to `high,critical` but can be overridden
