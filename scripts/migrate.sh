#!/bin/bash

set -e

echo "Migration main database"
uv run alembic upgrade head

echo "Migration test database"
TESTING=1 uv run alembic upgrade head

echo "Migration completed successfully"