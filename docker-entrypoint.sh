#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up and ready!"
}

# Function to check if Redis is ready
wait_for_redis() {
    echo "Waiting for Redis to be ready..."
    until redis-cli -h redis ping 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
    echo "Redis is up and ready!"
}

# Initialize the application
init_app() {
    echo "Running database migrations..."
    flask db upgrade
    
    echo "Creating admin user if not exists..."
    flask create-admin
    
    echo "Initialization completed successfully!"
}

# Main execution
echo "Starting application initialization..."

# Wait for services
wait_for_postgres
wait_for_redis

# Initialize application
init_app

echo "Starting application..."
exec "$@"
