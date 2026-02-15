FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY loki_mcp_server.py .
COPY formatting.py .
COPY tools/ tools/
COPY models/ models/

# Non-root user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# SSE transport for Docker, bind to all interfaces
ENV MCP_TRANSPORT=sse
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8000

CMD ["python", "loki_mcp_server.py"]
