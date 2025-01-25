# Use Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app/frontend

# Copy application code
COPY . /app/frontend

# Install dependencies
RUN uv sync --frozen

# Expose the port the app will use
EXPOSE 8501

# Define the command to run the application
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
