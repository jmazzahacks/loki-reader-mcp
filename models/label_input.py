from typing import Optional

from pydantic import BaseModel, Field


class GetLabelsInput(BaseModel):
    """Input for listing available Loki labels."""

    start: Optional[int] = Field(
        default=None,
        description="Start of the time range as a Unix timestamp in nanoseconds. "
        "Optional - if omitted, Loki uses its default range."
    )
    end: Optional[int] = Field(
        default=None,
        description="End of the time range as a Unix timestamp in nanoseconds. "
        "Optional - if omitted, Loki uses its default range."
    )


class GetLabelValuesInput(BaseModel):
    """Input for listing values of a specific Loki label."""

    label: str = Field(
        description="The label name to get values for, e.g. 'job' or 'container'"
    )
    start: Optional[int] = Field(
        default=None,
        description="Start of the time range as a Unix timestamp in nanoseconds"
    )
    end: Optional[int] = Field(
        default=None,
        description="End of the time range as a Unix timestamp in nanoseconds"
    )


class GetSeriesInput(BaseModel):
    """Input for listing unique label sets (series) matching selectors."""

    match: list[str] = Field(
        description="List of stream selectors to match, "
        "e.g. ['{job=\"myapp\"}', '{container=\"web\"}']"
    )
    start: Optional[int] = Field(
        default=None,
        description="Start of the time range as a Unix timestamp in nanoseconds"
    )
    end: Optional[int] = Field(
        default=None,
        description="End of the time range as a Unix timestamp in nanoseconds"
    )
