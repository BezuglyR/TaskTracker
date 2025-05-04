# Stage building
FROM python:3.13.3-slim AS build

# Copy the uv binary from a remote container image to the local build environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv configuration
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/panettone

# Copy dependency files for uv to resolve and lock dependencies
COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

# Use a cache mount to speed up dependency resolution
RUN --mount=type=cache,target=/root/.cache
RUN cd /_lock  && uv sync \
    --locked \
    --no-dev \
    --no-install-project

##########################################################################
# Final stage
FROM python:3.13.3-slim

# Add the tasktracker binary directory to the PATH
ENV PATH=/tasktracker/bin:$PATH

# Create a system group and user for the application
RUN groupadd -r tasktracker
RUN useradd -r -d /tasktracker -g tasktracker -N tasktracker

# Set the stop signal for the container
STOPSIGNAL SIGINT

# Clean up unnecessary files to reduce image size
RUN apt-get clean  # Clean up apt cache
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy the built application from the build stage
COPY --from=build --chown=tasktracker:tasktracker /tasktracker /tasktracker

# Switch to the tasktracker user and set the working directory
USER tasktracker
WORKDIR /tasktracker

# Copy application files to the container
COPY /app/ app/
#COPY /tests/ tests/
COPY .env app/
COPY alembic.ini app/

# Add the wait-for-it script for service dependency management
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh