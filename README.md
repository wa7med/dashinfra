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

## Production Deployment

The production setup uses:
- Multi-stage Docker builds
- Non-root user for security
- Health checks for all services
- Gunicorn as WSGI server
- Redis for caching
- PostgreSQL for data persistence

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.