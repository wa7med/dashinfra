# DashInfra

A modern web-based dashboard for managing devices and servers, built with Flask and PostgreSQL.

## Features

- User Authentication and Authorization
- Device Management System
- Real-time Activity Monitoring
- Responsive Design
- Dark/Light Theme Support
- Pagination Support
- Secure Password Management
- Docker Support

## Quick Start (Production)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dashinfra.git
cd dashinfra
```

2. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Start the application:
```bash
docker-compose up -d
```

The application will be available at http://localhost:80

## Development Setup

For development, use the development compose file:

```bash
docker-compose -f docker-compose-dev.yml up --build
```

The development server will be available at http://localhost:5000

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