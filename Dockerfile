FROM python:3.14-slim

WORKDIR /app

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-install-project

COPY . .

CMD ["uv", "run", "fastapi", "run"]