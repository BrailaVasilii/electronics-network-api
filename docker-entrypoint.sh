#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Electronics Network API...${NC}"

# Function to wait for database
wait_for_db() {
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    
    until python -c "
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        database=os.environ.get('DB_NAME', 'electronics_network_db')
    )
    conn.close()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
        echo -e "${YELLOW}Database is unavailable - sleeping...${NC}"
        sleep 2
    done
    
    echo -e "${GREEN}Database is ready!${NC}"
}

# Function to run migrations
run_migrations() {
    echo -e "${BLUE}Running database migrations...${NC}"
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    echo -e "${GREEN}Migrations completed!${NC}"
}

# Function to collect static files
collect_static() {
    echo -e "${BLUE}Collecting static files...${NC}"
    python manage.py collectstatic --noinput --clear
    echo -e "${GREEN}Static files collected!${NC}"
}

# Function to create superuser
create_superuser() {
    echo -e "${BLUE}Checking for superuser...${NC}"
    
    # Check if DJANGO_SUPERUSER_* environment variables are set
    if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = '$DJANGO_SUPERUSER_USERNAME'
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully!')
else:
    print(f'Superuser {username} already exists.')
EOF
        echo -e "${GREEN}Superuser check completed!${NC}"
    else
        echo -e "${YELLOW}Superuser environment variables not set. Skipping superuser creation.${NC}"
    fi
}

# Function to validate Django setup
validate_django() {
    echo -e "${BLUE}Validating Django setup...${NC}"
    python manage.py check --deploy
    echo -e "${GREEN}Django validation passed!${NC}"
}

# Main execution
main() {
    wait_for_db
    run_migrations
    collect_static
    create_superuser
    validate_django
    
    echo -e "${GREEN}Setup completed! Starting application...${NC}"
    
    # Execute the main command
    exec "$@"
}

# Handle signals
trap 'echo -e "${RED}Received SIGTERM, shutting down gracefully...${NC}"; exit 0' TERM

# Run main function
main "$@"