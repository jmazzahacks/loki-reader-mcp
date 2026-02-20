"""MCP tools for Loki log queries."""

import asyncio

from mcp.server.fastmcp import Context

from formatting import format_query_result, format_error
from models import QueryInput, QueryRangeInput
from loki_reader_core import LokiAuthError, LokiConnectionError, LokiQueryError


async def loki_query(params: QueryInput, ctx: Context) -> str:
    """Query Loki logs by application name.

    Auto-discovers the correct label for the application. Use 'severity'
    to filter by minimum log level and since_minutes/since_hours/since_days
    for a time window.

    Args:
        params: Query parameters including app, severity, limit, and since_*.
        ctx: MCP context with lifespan state.

    Returns:
        Formatted markdown string with query results or error message.
    """
    client = ctx.request_context.lifespan_context["client"]
    try:
        result = await asyncio.to_thread(
            client.query,
            app=params.app,
            severity=params.severity,
            limit=params.limit,
            since_minutes=params.since_minutes,
            since_hours=params.since_hours,
            since_days=params.since_days,
        )
        return format_query_result(result)
    except (LokiAuthError, LokiConnectionError, LokiQueryError) as exc:
        return _handle_loki_error(exc)
    except Exception as exc:
        return format_error(exc)


async def loki_query_range(params: QueryRangeInput, ctx: Context) -> str:
    """Execute a range LogQL query against Loki over a time window.

    Queries logs between a start and end timestamp. Use this for investigating
    issues within a specific time period.

    Both start and end are required and must be Unix timestamps in nanoseconds.
    To convert from seconds, multiply by 1_000_000_000. For example, to query
    the last hour: start = (now - 3600) * 1_000_000_000, end = now * 1_000_000_000.

    Args:
        params: Query parameters including logql, start, end, limit, direction.
        ctx: MCP context with lifespan state.

    Returns:
        Formatted markdown string with query results or error message.
    """
    client = ctx.request_context.lifespan_context["client"]
    try:
        result = await asyncio.to_thread(
            client.query_range,
            logql=params.logql,
            start=params.start,
            end=params.end,
            limit=params.limit,
            direction=params.direction,
        )
        return format_query_result(result)
    except (LokiAuthError, LokiConnectionError, LokiQueryError) as exc:
        return _handle_loki_error(exc)
    except Exception as exc:
        return format_error(exc)


def _handle_loki_error(exc: Exception) -> str:
    """Convert a Loki-specific exception to a user-friendly error message.

    Args:
        exc: A LokiAuthError, LokiConnectionError, or LokiQueryError.

    Returns:
        Descriptive error string.
    """
    if isinstance(exc, LokiAuthError):
        return "**Error:** Authentication failed. Check LOKI_USER/LOKI_PASS in your .env"
    if isinstance(exc, LokiConnectionError):
        return "**Error:** Connection failed. Check LOKI_URL and network connectivity."
    if isinstance(exc, LokiQueryError):
        return f"**Error:** Query failed: {exc}"
    return format_error(exc)
