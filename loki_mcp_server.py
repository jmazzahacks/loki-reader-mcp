"""Loki MCP Server - exposes Loki log queries as MCP tools."""

import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from loki_reader_core import LokiClient
from tools.query_tools import loki_query, loki_query_range
from tools.label_tools import loki_get_labels, loki_get_label_values, loki_get_series

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("loki_mcp")


def create_loki_client() -> LokiClient:
    """Create a LokiClient from environment variables.

    Loads .env file if present and builds the client from env vars.

    Returns:
        Configured LokiClient instance.

    Raises:
        SystemExit: If LOKI_URL is not set.
    """
    load_dotenv()

    url = os.getenv("LOKI_URL")
    if not url:
        logger.error("LOKI_URL environment variable is required")
        logger.error("Copy example.env to .env and fill in your values")
        sys.exit(1)

    user = os.getenv("LOKI_USER")
    password = os.getenv("LOKI_PASS")
    ca_cert = os.getenv("LOKI_CA_CERT")
    org_id = os.getenv("LOKI_ORG_ID")

    auth: Optional[tuple[str, str]] = None
    if user and password:
        auth = (user, password)

    logger.info("Loki connection: url=%s, auth=%s, ca_cert=%s, org_id=%s",
                url,
                "yes" if auth else "none",
                ca_cert if ca_cert else "none",
                org_id if org_id else "none")

    return LokiClient(
        base_url=url,
        auth=auth,
        ca_cert=ca_cert,
        org_id=org_id,
    )


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage the LokiClient lifecycle.

    Creates a single LokiClient on startup and closes it on shutdown.

    Args:
        server: The FastMCP server instance.

    Yields:
        Dict with 'client' key containing the LokiClient.
    """
    client = create_loki_client()
    logger.info("LokiClient created, server ready")
    try:
        yield {"client": client}
    finally:
        client.close()
        logger.info("LokiClient closed")


tool_annotations = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}

mcp = FastMCP("loki_mcp", lifespan=app_lifespan)

mcp.tool(
    name="loki_query",
    description="Execute an instant LogQL query against Loki at a single point in time. "
    "Use for quick checks like 'show latest logs for this app'. "
    "Timestamps are Unix nanoseconds (seconds * 1_000_000_000).",
    annotations=tool_annotations,
)(loki_query)

mcp.tool(
    name="loki_query_range",
    description="Execute a range LogQL query against Loki over a time window. "
    "Use for investigating issues within a specific time period. "
    "Both start and end are required Unix timestamps in nanoseconds "
    "(seconds * 1_000_000_000).",
    annotations=tool_annotations,
)(loki_query_range)

mcp.tool(
    name="loki_get_labels",
    description="List all available label names in Loki. "
    "Returns labels like 'job', 'container', 'namespace', etc. "
    "Optionally filter by time range (nanosecond timestamps).",
    annotations=tool_annotations,
)(loki_get_labels)

mcp.tool(
    name="loki_get_label_values",
    description="Get all values for a specific Loki label. "
    "For example, get all values for 'job' to see what apps are logging. "
    "Optionally filter by time range (nanosecond timestamps).",
    annotations=tool_annotations,
)(loki_get_label_values)

mcp.tool(
    name="loki_get_series",
    description="Get unique label sets (series) matching stream selectors. "
    "Returns distinct label combinations for matching streams. "
    "Useful for discovering what log streams exist.",
    annotations=tool_annotations,
)(loki_get_series)


if __name__ == "__main__":
    mcp.run()
