
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Install uv
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
#uv creates a virtual environment at /app/.venv

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies into a project-local virtual environment
RUN uv sync --frozen --no-install-project

# At this stage, we have copied only pyproject.toml and uv.lock. We haven't copied your actual application source code yet.
# We only want to install the dependencies first.
# Also, uv sync creates a virtual environment at /app/.venv by default.
# Stage 2: Final runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make virtual environment executables available
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source code
COPY . .

# Application port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#0.0.0.0 means the application listens on all interfaces; 
#this is necessary for Docker containers to be accessible from outside the container.