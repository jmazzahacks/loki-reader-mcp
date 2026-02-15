# loki-reader-mcp

Python MCP server that exposes Grafana Loki log query capabilities as tools for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (or any MCP client). Uses [loki-reader-core](https://github.com/jmazzahacks/loki-reader-core) for all Loki communication.

## Tools

| Tool | Description |
|------|-------------|
| `loki_query` | Instant query at a single point in time |
| `loki_query_range` | Range query across a time window |
| `loki_get_labels` | List all available label names |
| `loki_get_label_values` | Get all values for a specific label |
| `loki_get_series` | Get unique label sets matching stream selectors |

All tools return formatted markdown and include error handling for auth, connection, and query failures.

## Setup

### 1. Create a virtual environment

```bash
python -m venv .
source bin/activate
```

### 2. Install dependencies

```bash
pip install mcp[cli] loki-reader-core python-dotenv pydantic
```

For local development against loki-reader-core:

```bash
pip install -e ../loki-reader-core
```

### 3. Configure environment

```bash
cp example.env .env
```

Edit `.env` with your Loki connection details:

| Variable | Required | Description |
|----------|----------|-------------|
| `LOKI_URL` | Yes | Base URL of the Loki server |
| `LOKI_USER` | No | Username for basic auth |
| `LOKI_PASS` | No | Password for basic auth |
| `LOKI_CA_CERT` | No | Path to CA certificate PEM file |
| `LOKI_ORG_ID` | No | X-Scope-OrgID for multi-tenant setups |

### 4. Run tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Usage with Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "loki": {
      "command": "/path/to/loki-reader-mcp/bin/python",
      "args": ["/path/to/loki-reader-mcp/loki_mcp_server.py"]
    }
  }
}
```

Once configured, Claude Code can query your Loki logs directly using natural language. All timestamps use Unix nanoseconds (Loki's native format).

## Project Structure

```
loki_mcp_server.py       # FastMCP entry point with lifespan and tool registration
formatting.py            # Markdown response formatters
models/
  query_input.py         # QueryInput, QueryRangeInput (Pydantic)
  label_input.py         # GetLabelsInput, GetLabelValuesInput, GetSeriesInput
tools/
  query_tools.py         # loki_query, loki_query_range
  label_tools.py         # loki_get_labels, loki_get_label_values, loki_get_series
tests/
  test_models.py         # Input validation tests
  test_tools.py          # Tool tests with mocked LokiClient
```

## License

MIT
