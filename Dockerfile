FROM python:3.13.3-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /tasktracker

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy application files to the container
COPY /app/ app/
COPY .env .
COPY alembic.ini .
COPY entrypoint.sh .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Add the tasktracker binary directory to the PATH
ENV PATH=/tasktracker/.venv/bin:$PATH

# Create a system group and user for the application
RUN groupadd -r tasktracker
RUN useradd -r -d /app -g tasktracker -N tasktracker

# Set the stop signal for the container
STOPSIGNAL SIGINT

# Switch to the tasktracker user and set the working directory
USER tasktracker

ENTRYPOINT ["bash", "./entrypoint.sh"]