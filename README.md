# 2048 Dashboard

A modern web-based dashboard for monitoring and managing servers and devices. Built with Flask and SQLAlchemy, featuring a responsive design that works seamlessly in both light and dark modes.

## Features

- **User Authentication**
  - Secure login system with Flask-Login
  - Role-based access control (Admin/User)
  - Password change functionality
  - User profile management

- **Device Management**
  - Add and monitor servers and devices
  - Real-time status tracking
  - Device categorization (server, device, camera)
  - Detailed device information display

- **Dashboard Interface**
  - Modern, responsive design
  - Dark/Light theme toggle
  - Real-time notifications system
  - Search functionality
  - User-friendly navigation

- **Admin Features**
  - User management
  - System-wide monitoring
  - Administrative controls

## Technology Stack

- **Backend**
  - Python 3.x
  - Flask (Web Framework)
  - SQLAlchemy (Database ORM)
  - Flask-Login (Authentication)

- **Frontend**
  - HTML5/CSS3
  - JavaScript
  - Font Awesome Icons
  - Responsive Design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/2048-dashboard.git
cd 2048-dashboard
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

## Configuration

The application can be configured through environment variables or a `.env` file:

- `FLASK_APP`: Set to `app.py`
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Your secret key for session management
- `DATABASE_URL`: Your database connection string

## Usage

1. Access the application at `http://localhost:5000`
2. Login with your credentials
3. Navigate through the dashboard using the sidebar
4. Add and monitor devices as needed
5. Use the theme toggle for comfortable viewing in any lighting condition

## Security

- Password hashing using Werkzeug
- Session management with Flask-Login
- CSRF protection
- Role-based access control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.