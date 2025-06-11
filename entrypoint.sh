#!/bin/bash

echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ PostgreSQL is up!"

python manage.py migrate