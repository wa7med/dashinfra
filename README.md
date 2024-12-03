# 2048 Web Dashboard

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

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.11+
- Redis (optional, for caching)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/2048-dashboard.git
cd 2048-dashboard
```

2. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at http://localhost:5000

## Manual Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
flask db upgrade
```

4. Run the application:
```bash
flask run
```

## Environment Variables

- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `REDIS_URL`: Redis connection string (optional)
- `MAIL_SERVER`: SMTP server for emails
- `MAIL_PORT`: SMTP port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password

## Docker Deployment

1. Build the image:
```bash
docker build -t yourusername/2048-dashboard:latest .
```

2. Push to Docker Hub:
```bash
docker push yourusername/2048-dashboard:latest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

- All passwords are hashed using strong algorithms
- CSRF protection enabled
- Input validation and sanitization
- Secure session management
- Environment variable management for sensitive data

## Support

For support, please open an issue in the GitHub repository.