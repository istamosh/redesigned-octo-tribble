# pull the python
FROM python:3.12.11-slim-bookworm

# pull UV
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
# Copy the project into the image
COPY . .

RUN uv sync --locked

EXPOSE 8000

# Presuming there is a `my_app` command provided by the project
# gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
CMD ["uv", "run", "gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]

# docker run -p 8000:8000 --name uvprodcontainer uvproduction