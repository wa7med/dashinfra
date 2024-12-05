# Test Lab Infrastructure Dashboard

A modern web-based dashboard for managing test lab infrastructure and devices, built with Flask and PostgreSQL.

## Features

- User Authentication and Authorization
- Test Lab Inventory Management
- Real-time Activity Monitoring
- Redis Caching System
- Responsive Design
- Dark/Light Theme Support
- Pagination Support
- Secure Password Management
- Docker Support

## Quick Start

1. Ensure Docker is installed on your system

2. Copy docker-compose.yml to your deployment directory

3. Start the application:
```bash
docker-compose up -d
```

The application will be available at http://localhost:80

## Environment Variables

Required environment variables in .env:
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `REDIS_URL`: Redis connection string

## Architecture

- Backend: Flask (Python)
- Database: PostgreSQL
- Cache: Redis
- Authentication: Flask-Login
- ORM: SQLAlchemy
- WSGI Server: Gunicorn
- Container: Docker

## Deployment Features

The Deployment setup uses:
- Multi-stage Docker builds
- Non-root user for security
- Health checks for all services
- Gunicorn as WSGI server
- Redis for caching
- PostgreSQL for data persistence

## Data Persistence

By default, the PostgreSQL data is stored in a Docker volume. While this works, the data will be lost if you run `docker-compose down -v`. To make your data truly persistent, follow these steps:

1. Create a local data directory:
```bash
mkdir -p data/postgres
```

2. Modify the `volumes` section in your `docker-compose.yml` for the `db` service:
```yaml
services:
  db:
    volumes:
      - ./data/postgres:/var/lib/postgresql/data  # Changed from postgres_data:/var/lib/postgresql/data
```

3. Remove the `volumes` section at the bottom of the file that defines `postgres_data`.

Now your PostgreSQL data will be stored in the local `data/postgres` directory and will persist even when running `docker-compose down -v`.


## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.