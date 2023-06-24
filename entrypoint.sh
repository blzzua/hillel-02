#!/bin/bash

set -e

echo "ENTRYPOINT"
python manage.py migrate
python manage.py collectstatic --noinput

if python manage.py shell -c "from accounts.models import User; exit(0) if User.objects.filter(is_superuser=True).exists() else exit(1)"; then
    echo "Superuser already exists. Skipping creation."
else
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input
fi

exec "$@"
