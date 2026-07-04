import os
import json
import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Design Choice: We use FastMCP from the official MCP Python SDK to quickly scaffold a minimal
# Model Context Protocol server. FastMCP handles the protocol boilerplate so we can focus on
# defining meaningful tools that agents or LLMs can invoke.
mcp = FastMCP("SpotterWeeklyReports")

# Design Choice: Write reports to a local `reports/` directory alongside the project.
# This avoids requiring external credentials (e.g., Google Sheets OAuth) during development,
# making the system self-contained and easy to test. The path is resolved relative to this file
# so it works regardless of the working directory the server is launched from.
REPORTS_DIR = Path(__file__).parent.parent / "reports"


@mcp.tool()
def push_weekly_report(report_content: str, user_id: int) -> str:
    """
    Persists the weekly progress report to a local JSON file.

    Args:
        report_content: The LLM-generated weekly review text produced by ProgramAgent.
        user_id:        The user's database ID, used to namespace the report file.

    Returns:
        A status message confirming the file path written, or an error description.

    Design Choice: Accepting `user_id` lets us generate per-user report files
    (e.g. weekly_report_42.json) without collisions in a multi-user environment.
    """
    # Ensure the reports directory exists — create it silently if not present.
    # Design Choice: We never store secrets here; the only data persisted is the
    # user-supplied report content and metadata derived from runtime values.
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Build the report payload with timestamp metadata so the file is self-documenting.
        payload = {
            "user_id": user_id,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "report": report_content,
        }

        # One file per user — overwrite on each weekly run so the file always reflects
        # the latest state. A future iteration could append to a list for a historical log.
        report_path = REPORTS_DIR / f"weekly_report_{user_id}.json"

        with report_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return f"Success: Weekly report written to {report_path.resolve()}"

    except Exception as e:
        # Surface errors clearly so the calling agent can decide whether to retry.
        return f"Error writing weekly report: {str(e)}"


if __name__ == "__main__":
    # Design Choice: stdio transport is the standard for local MCP servers.
    # It lets any compliant host (Claude Desktop, ADK, etc.) spin up this process
    # and communicate over stdin/stdout without needing a network port.
    mcp.run(transport="stdio")
