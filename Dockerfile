FROM python:3.13.3-slim

# Install uv
RUN pip install uv --no-cache-dir

WORKDIR /tasktracker

# Copy application files to the container
COPY /app/ app/
COPY pyproject.toml .
COPY uv.lock .
COPY .env .
COPY alembic.ini .

# Add the tasktracker binary directory to the PATH
ENV PATH=/tasktracker/.venv/bin:$PATH

# Install system dependencies
RUN uv sync --locked --no-dev

# Create a system group and user for the application
RUN groupadd -r tasktracker
RUN useradd -r -d /app -g tasktracker -N tasktracker

# Set the stop signal for the container
STOPSIGNAL SIGINT

# Switch to the tasktracker user and set the working directory
USER tasktracker

ENTRYPOINT ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "app.main:app"]