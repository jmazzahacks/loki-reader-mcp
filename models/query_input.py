from typing import Optional

from pydantic import BaseModel, Field


class QueryInput(BaseModel):
    """Input for querying Loki logs by application name."""

    app: str = Field(
        description="Application name to search for. Auto-discovers the correct "
        "label (application, app, job, service, etc.)"
    )
    severity: Optional[str] = Field(
        default=None,
        description="Minimum severity level. Includes this level and above. "
        "Values: trace, debug, info, warn/warning, error, fatal/critical"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=5000,
        description="Maximum number of log entries to return"
    )
    since_minutes: Optional[int] = Field(
        default=None,
        description="Return logs from the last N minutes"
    )
    since_hours: Optional[int] = Field(
        default=None,
        description="Return logs from the last N hours"
    )
    since_days: Optional[int] = Field(
        default=None,
        description="Return logs from the last N days"
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
