"""Shared response formatting helpers for MCP tool output."""

from datetime import datetime, timezone

from loki_reader_core import QueryResult
from loki_reader_core.utils import ns_to_seconds


def format_query_result(result: QueryResult) -> str:
    """Format a QueryResult as readable markdown text.

    Handles all three Loki result types: streams, matrix, and vector.

    Args:
        result: The QueryResult from a Loki query.

    Returns:
        Markdown-formatted string with stats and log entries or metric values.
    """
    if result.result_type in ("matrix", "vector"):
        return _format_metric_result(result)
    return _format_stream_result(result)


def _format_stream_result(result: QueryResult) -> str:
    """Format a streams-type QueryResult as readable markdown.

    Args:
        result: The QueryResult with log streams.

    Returns:
        Markdown-formatted string with stats and log entries.
    """
    lines: list[str] = []

    lines.append(f"**Status:** {result.status}")
    lines.append(f"**Streams:** {len(result.streams)}")
    lines.append(f"**Total entries:** {result.total_entries}")

    if result.stats:
        lines.append(f"**Exec time:** {result.stats.exec_time_seconds:.3f}s")
        bytes_display = _format_bytes(result.stats.bytes_processed)
        lines.append(f"**Bytes processed:** {bytes_display}")

    if not result.streams:
        lines.append("\nNo log entries found.")
        return "\n".join(lines)

    for stream in result.streams:
        labels_str = ", ".join(
            f"{k}={v}" for k, v in stream.labels.items()
        )
        lines.append(f"\n---\n### Stream: {{{labels_str}}}")
        lines.append(f"Entries: {len(stream.entries)}\n")

        for entry in stream.entries:
            timestamp_str = _format_timestamp(entry.timestamp)
            lines.append(f"`{timestamp_str}` {entry.message}")

    return "\n".join(lines)


def _format_metric_result(result: QueryResult) -> str:
    """Format a matrix/vector-type QueryResult as readable markdown.

    Args:
        result: The QueryResult with metric series.

    Returns:
        Markdown-formatted string with stats and metric values.
    """
    lines: list[str] = []

    lines.append(f"**Status:** {result.status}")
    lines.append(f"**Result type:** {result.result_type}")
    lines.append(f"**Series:** {len(result.metric_series)}")
    lines.append(f"**Total samples:** {result.total_samples}")

    if result.stats:
        lines.append(f"**Exec time:** {result.stats.exec_time_seconds:.3f}s")
        bytes_display = _format_bytes(result.stats.bytes_processed)
        lines.append(f"**Bytes processed:** {bytes_display}")

    if not result.metric_series:
        lines.append("\nNo metric data found.")
        return "\n".join(lines)

    for series in result.metric_series:
        labels_str = ", ".join(
            f"{k}={v}" for k, v in series.labels.items()
        )
        lines.append(f"\n---\n### Series: {{{labels_str}}}")
        lines.append(f"Samples: {len(series.samples)}\n")

        for sample in series.samples:
            timestamp_str = _format_timestamp(sample.timestamp)
            lines.append(f"`{timestamp_str}` **{sample.value}**")

    return "\n".join(lines)


def format_labels(labels: list[str]) -> str:
    """Format a list of label names as a bulleted markdown list.

    Args:
        labels: List of label name strings.

    Returns:
        Markdown-formatted bulleted list.
    """
    if not labels:
        return "No labels found."

    lines = [f"**Available labels ({len(labels)}):**\n"]
    for label in sorted(labels):
        lines.append(f"- `{label}`")
    return "\n".join(lines)


def format_label_values(label: str, values: list[str]) -> str:
    """Format label values as a bulleted markdown list.

    Args:
        label: The label name.
        values: List of values for that label.

    Returns:
        Markdown-formatted bulleted list with header.
    """
    if not values:
        return f"No values found for label `{label}`."

    lines = [f"**Values for `{label}` ({len(values)}):**\n"]
    for value in sorted(values):
        lines.append(f"- `{value}`")
    return "\n".join(lines)


def format_series(series: list[dict]) -> str:
    """Format series label sets as readable text.

    Args:
        series: List of label dictionaries from get_series.

    Returns:
        Markdown-formatted series list.
    """
    if not series:
        return "No matching series found."

    lines = [f"**Matching series ({len(series)}):**\n"]
    for label_set in series:
        parts = ", ".join(f"{k}={v}" for k, v in label_set.items())
        lines.append(f"- {{{parts}}}")
    return "\n".join(lines)


def format_error(error: Exception) -> str:
    """Format an exception as a consistent error message.

    Args:
        error: The exception to format.

    Returns:
        Error message string.
    """
    return f"**Error:** {type(error).__name__}: {error}"


def _format_timestamp(nanoseconds: int) -> str:
    """Convert a nanosecond timestamp to a human-readable UTC string.

    Args:
        nanoseconds: Unix timestamp in nanoseconds.

    Returns:
        Formatted datetime string like '2024-01-15 14:30:45 UTC'.
    """
    seconds = ns_to_seconds(nanoseconds)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _format_bytes(byte_count: int) -> str:
    """Format a byte count into a human-readable string.

    Args:
        byte_count: Number of bytes.

    Returns:
        Formatted string like '1.5 MB' or '320 KB'.
    """
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    if byte_count < 1024 * 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.1f} MB"
    return f"{byte_count / (1024 * 1024 * 1024):.1f} GB"
