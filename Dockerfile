# Minimal image for the example MCP server (stdio). Standard library only.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY server/ /app/server/
COPY examples/ /app/examples/
RUN useradd --no-create-home --uid 10001 mcp
USER mcp
ENTRYPOINT ["python", "/app/server/mcp_server.py"]
