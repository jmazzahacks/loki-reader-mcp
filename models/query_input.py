from typing import Optional

from pydantic import BaseModel, Field


class QueryInput(BaseModel):
    """Input for an instant Loki query at a single point in time."""

    logql: str = Field(
        description="LogQL query string, e.g. '{job=\"myapp\"} |= \"error\"'"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=5000,
        description="Maximum number of log entries to return"
    )
    time: Optional[int] = Field(
        default=None,
        description="Unix timestamp in nanoseconds for the query evaluation point. "
        "Defaults to now if omitted."
    )


class QueryRangeInput(BaseModel):
    """Input for a Loki range query across a time window."""

    logql: str = Field(
        description="LogQL query string, e.g. '{job=\"myapp\"} |= \"error\"'"
    )
    start: int = Field(
        description="Start of the time range as a Unix timestamp in nanoseconds"
    )
    end: int = Field(
        description="End of the time range as a Unix timestamp in nanoseconds"
    )
    limit: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Maximum number of log entries to return"
    )
    direction: str = Field(
        default="backward",
        pattern="^(forward|backward)$",
        description="Sort order: 'backward' (newest first) or 'forward' (oldest first)"
    )
