#!/bin/sh

set -e

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Starting server..."
# Запускаем команду из Dockerfile
exec "$@"
