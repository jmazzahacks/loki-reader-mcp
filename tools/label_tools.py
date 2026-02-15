"""MCP tools for Loki label and series queries."""

import asyncio

from mcp.server.fastmcp import Context

from formatting import format_labels, format_label_values, format_series, format_error
from models import GetLabelsInput, GetLabelValuesInput, GetSeriesInput
from loki_reader_core import LokiAuthError, LokiConnectionError, LokiQueryError


async def loki_get_labels(params: GetLabelsInput, ctx: Context) -> str:
    """List all available label names in Loki.

    Returns the set of label names that exist across all log streams.
    Optionally filter by time range using start/end timestamps in nanoseconds.

    Args:
        params: Optional start/end time range.
        ctx: MCP context with lifespan state.

    Returns:
        Formatted markdown list of label names or error message.
    """
    client = ctx.request_context.lifespan_context["client"]
    try:
        labels = await asyncio.to_thread(
            client.get_labels,
            start=params.start,
            end=params.end,
        )
        return format_labels(labels)
    except (LokiAuthError, LokiConnectionError, LokiQueryError) as exc:
        return _handle_loki_error(exc)
    except Exception as exc:
        return format_error(exc)


async def loki_get_label_values(params: GetLabelValuesInput, ctx: Context) -> str:
    """Get all values for a specific label in Loki.

    For example, get all values for the 'job' label to see what applications
    are logging. Optionally filter by time range.

    Args:
        params: Label name and optional start/end time range.
        ctx: MCP context with lifespan state.

    Returns:
        Formatted markdown list of label values or error message.
    """
    client = ctx.request_context.lifespan_context["client"]
    try:
        values = await asyncio.to_thread(
            client.get_label_values,
            label=params.label,
            start=params.start,
            end=params.end,
        )
        return format_label_values(params.label, values)
    except (LokiAuthError, LokiConnectionError, LokiQueryError) as exc:
        return _handle_loki_error(exc)
    except Exception as exc:
        return format_error(exc)


async def loki_get_series(params: GetSeriesInput, ctx: Context) -> str:
    """Get unique label sets (series) matching one or more stream selectors.

    Returns the distinct combinations of labels that match the given selectors.
    Useful for discovering what log streams exist. Optionally filter by time range.

    Args:
        params: List of match selectors and optional start/end time range.
        ctx: MCP context with lifespan state.

    Returns:
        Formatted markdown list of series or error message.
    """
    client = ctx.request_context.lifespan_context["client"]
    try:
        series = await asyncio.to_thread(
            client.get_series,
            match=params.match,
            start=params.start,
            end=params.end,
        )
        return format_series(series)
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
