"""Tests for Pydantic input models."""

import pytest
from pydantic import ValidationError

from models.query_input import QueryInput, QueryRangeInput
from models.label_input import GetLabelsInput, GetLabelValuesInput, GetSeriesInput


class TestQueryInput:

    def test_minimal_valid(self) -> None:
        model = QueryInput(logql='{job="myapp"}')
        assert model.logql == '{job="myapp"}'
        assert model.limit == 100
        assert model.time is None

    def test_all_fields(self) -> None:
        model = QueryInput(logql='{job="myapp"}', limit=50, time=1700000000000000000)
        assert model.limit == 50
        assert model.time == 1700000000000000000

    def test_missing_logql_raises(self) -> None:
        with pytest.raises(ValidationError):
            QueryInput()

    def test_limit_too_low(self) -> None:
        with pytest.raises(ValidationError):
            QueryInput(logql='{job="myapp"}', limit=0)

    def test_limit_too_high(self) -> None:
        with pytest.raises(ValidationError):
            QueryInput(logql='{job="myapp"}', limit=10000)


class TestQueryRangeInput:

    def test_minimal_valid(self) -> None:
        model = QueryRangeInput(
            logql='{job="myapp"}',
            start=1700000000000000000,
            end=1700003600000000000,
        )
        assert model.logql == '{job="myapp"}'
        assert model.limit == 1000
        assert model.direction == "backward"

    def test_all_fields(self) -> None:
        model = QueryRangeInput(
            logql='{job="myapp"}',
            start=1700000000000000000,
            end=1700003600000000000,
            limit=500,
            direction="forward",
        )
        assert model.limit == 500
        assert model.direction == "forward"

    def test_missing_start_raises(self) -> None:
        with pytest.raises(ValidationError):
            QueryRangeInput(logql='{job="myapp"}', end=1700003600000000000)

    def test_missing_end_raises(self) -> None:
        with pytest.raises(ValidationError):
            QueryRangeInput(logql='{job="myapp"}', start=1700000000000000000)

    def test_invalid_direction(self) -> None:
        with pytest.raises(ValidationError):
            QueryRangeInput(
                logql='{job="myapp"}',
                start=1700000000000000000,
                end=1700003600000000000,
                direction="sideways",
            )

    def test_limit_bounds(self) -> None:
        with pytest.raises(ValidationError):
            QueryRangeInput(
                logql='{job="myapp"}',
                start=1700000000000000000,
                end=1700003600000000000,
                limit=0,
            )
        with pytest.raises(ValidationError):
            QueryRangeInput(
                logql='{job="myapp"}',
                start=1700000000000000000,
                end=1700003600000000000,
                limit=10000,
            )


class TestGetLabelsInput:

    def test_defaults(self) -> None:
        model = GetLabelsInput()
        assert model.start is None
        assert model.end is None

    def test_with_time_range(self) -> None:
        model = GetLabelsInput(
            start=1700000000000000000,
            end=1700003600000000000,
        )
        assert model.start == 1700000000000000000
        assert model.end == 1700003600000000000


class TestGetLabelValuesInput:

    def test_minimal_valid(self) -> None:
        model = GetLabelValuesInput(label="job")
        assert model.label == "job"
        assert model.start is None
        assert model.end is None

    def test_missing_label_raises(self) -> None:
        with pytest.raises(ValidationError):
            GetLabelValuesInput()

    def test_with_time_range(self) -> None:
        model = GetLabelValuesInput(
            label="container",
            start=1700000000000000000,
            end=1700003600000000000,
        )
        assert model.label == "container"
        assert model.start == 1700000000000000000


class TestGetSeriesInput:

    def test_minimal_valid(self) -> None:
        model = GetSeriesInput(match=['{job="myapp"}'])
        assert model.match == ['{job="myapp"}']
        assert model.start is None

    def test_multiple_matchers(self) -> None:
        model = GetSeriesInput(match=['{job="a"}', '{job="b"}'])
        assert len(model.match) == 2

    def test_missing_match_raises(self) -> None:
        with pytest.raises(ValidationError):
            GetSeriesInput()
