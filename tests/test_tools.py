"""Tests for MCP tools with mocked LokiClient."""

from unittest.mock import MagicMock, patch

import pytest

from loki_reader_core import (
    LokiAuthError,
    LokiConnectionError,
    LokiQueryError,
    LogEntry,
    LogStream,
    QueryResult,
    QueryStats,
)

from tools.query_tools import loki_query, loki_query_range
from tools.label_tools import loki_get_labels, loki_get_label_values, loki_get_series
from models import (
    QueryInput,
    QueryRangeInput,
    GetLabelsInput,
    GetLabelValuesInput,
    GetSeriesInput,
)


def make_mock_ctx(client: MagicMock) -> MagicMock:
    """Create a mock MCP context with a client in the lifespan state."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = {"client": client}
    return ctx


def make_query_result(
    entries: list[tuple[int, str]],
    labels: dict[str, str] | None = None,
) -> QueryResult:
    """Build a QueryResult with a single stream for testing."""
    if labels is None:
        labels = {"job": "testapp"}
    log_entries = [LogEntry(timestamp=ts, message=msg) for ts, msg in entries]
    stream = LogStream(labels=labels, entries=log_entries)
    stats = QueryStats(
        bytes_processed=1024,
        lines_processed=len(entries),
        exec_time_seconds=0.05,
    )
    return QueryResult(status="success", streams=[stream], stats=stats)


class TestLokiQuery:

    @pytest.mark.asyncio
    async def test_successful_query(self) -> None:
        client = MagicMock()
        result = make_query_result([
            (1700000000000000000, "test log message"),
        ])
        client.query.return_value = result
        ctx = make_mock_ctx(client)

        params = QueryInput(logql='{job="testapp"}')

        with patch("tools.query_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_query(params, ctx)

        assert "success" in output
        assert "test log message" in output
        assert "1 entries" in output or "Total entries:** 1" in output
        client.query.assert_called_once_with(
            logql='{job="testapp"}',
            limit=100,
            time=None,
        )

    @pytest.mark.asyncio
    async def test_auth_error(self) -> None:
        client = MagicMock()
        client.query.side_effect = LokiAuthError("401 Unauthorized")
        ctx = make_mock_ctx(client)

        params = QueryInput(logql='{job="testapp"}')

        with patch("tools.query_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_query(params, ctx)

        assert "Authentication failed" in output

    @pytest.mark.asyncio
    async def test_connection_error(self) -> None:
        client = MagicMock()
        client.query.side_effect = LokiConnectionError("Connection refused")
        ctx = make_mock_ctx(client)

        params = QueryInput(logql='{job="testapp"}')

        with patch("tools.query_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_query(params, ctx)

        assert "Connection failed" in output

    @pytest.mark.asyncio
    async def test_query_error(self) -> None:
        client = MagicMock()
        client.query.side_effect = LokiQueryError("parse error")
        ctx = make_mock_ctx(client)

        params = QueryInput(logql="bad query")

        with patch("tools.query_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_query(params, ctx)

        assert "Query failed" in output


class TestLokiQueryRange:

    @pytest.mark.asyncio
    async def test_successful_range_query(self) -> None:
        client = MagicMock()
        result = make_query_result([
            (1700000000000000000, "log line 1"),
            (1700000001000000000, "log line 2"),
        ])
        client.query_range.return_value = result
        ctx = make_mock_ctx(client)

        params = QueryRangeInput(
            logql='{job="testapp"}',
            start=1700000000000000000,
            end=1700003600000000000,
        )

        with patch("tools.query_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_query_range(params, ctx)

        assert "log line 1" in output
        assert "log line 2" in output
        client.query_range.assert_called_once_with(
            logql='{job="testapp"}',
            start=1700000000000000000,
            end=1700003600000000000,
            limit=1000,
            direction="backward",
        )


class TestLokiGetLabels:

    @pytest.mark.asyncio
    async def test_successful_get_labels(self) -> None:
        client = MagicMock()
        client.get_labels.return_value = ["job", "container", "namespace"]
        ctx = make_mock_ctx(client)

        params = GetLabelsInput()

        with patch("tools.label_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_get_labels(params, ctx)

        assert "container" in output
        assert "job" in output
        assert "namespace" in output

    @pytest.mark.asyncio
    async def test_empty_labels(self) -> None:
        client = MagicMock()
        client.get_labels.return_value = []
        ctx = make_mock_ctx(client)

        params = GetLabelsInput()

        with patch("tools.label_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_get_labels(params, ctx)

        assert "No labels found" in output


class TestLokiGetLabelValues:

    @pytest.mark.asyncio
    async def test_successful_get_values(self) -> None:
        client = MagicMock()
        client.get_label_values.return_value = ["app1", "app2", "app3"]
        ctx = make_mock_ctx(client)

        params = GetLabelValuesInput(label="job")

        with patch("tools.label_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_get_label_values(params, ctx)

        assert "job" in output
        assert "app1" in output
        assert "app2" in output


class TestLokiGetSeries:

    @pytest.mark.asyncio
    async def test_successful_get_series(self) -> None:
        client = MagicMock()
        client.get_series.return_value = [
            {"job": "app1", "container": "web"},
            {"job": "app2", "container": "worker"},
        ]
        ctx = make_mock_ctx(client)

        params = GetSeriesInput(match=['{job=~"app.*"}'])

        with patch("tools.label_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_get_series(params, ctx)

        assert "app1" in output
        assert "app2" in output
        assert "Matching series (2)" in output

    @pytest.mark.asyncio
    async def test_empty_series(self) -> None:
        client = MagicMock()
        client.get_series.return_value = []
        ctx = make_mock_ctx(client)

        params = GetSeriesInput(match=['{job="nonexistent"}'])

        with patch("tools.label_tools.asyncio.to_thread", side_effect=_call_sync):
            output = await loki_get_series(params, ctx)

        assert "No matching series found" in output


async def _call_sync(func, *args, **kwargs):
    """Helper to call a sync function directly instead of using asyncio.to_thread."""
    return func(*args, **kwargs)
