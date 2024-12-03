from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import db, User, Device
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 minutes
# Disable secure cookie in development
if app.debug:
    app.config['SESSION_COOKIE_SECURE'] = False
else:
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/dashinfra'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

# Make sure tables are created when the app starts
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
@login_required
def dashboard():
    # Get all devices for everyone
    devices = Device.query.all()
    
    # Get a dictionary of usernames for all device owners
    user_ids = {device.user_id for device in devices}
    users = User.query.filter(User.id.in_(user_ids)).all()
    user_dict = {user.id: user.username for user in users}
    
    return render_template('dashboard.html', 
                         devices=devices, 
                         user_dict=user_dict, 
                         current_user=current_user)

class AddServerForm(FlaskForm):
    server_name = StringField('Server Name', validators=[DataRequired()], name='server-name')
    server_ip = StringField('Server IP', validators=[DataRequired()], name='server-ip')
    server_type = SelectField('Server Type', 
                            choices=[('server', 'Server'), 
                                   ('device', 'Device'), 
                                   ('camera', 'Camera')],
                            validators=[DataRequired()],
                            name='server-type')
    server_description = TextAreaField('Server Description', name='server-description')

@app.route('/add-server', methods=['GET', 'POST'])
@login_required
def add_server():
    form = AddServerForm()
    if request.method == 'POST':
        print("POST request received")
        print("Form data:", request.form)
        if form.validate_on_submit():
            try:
                current_time = datetime.utcnow()
                # Create new device
                new_device = Device(
                    name=request.form['server-name'],
                    ip_address=request.form['server-ip'],
                    device_type=request.form['server-type'],
                    description=request.form['server-description'],
                    user_id=current_user.id,
                    status='active',
                    created_at=current_time,
                    updated_at=current_time
                )
                print("Adding device to session")
                db.session.add(new_device)
                print("Committing to database")
                db.session.commit()
                print("Device added successfully with ID:", new_device.id)
                flash('Device added successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                print("Error occurred:", str(e))
                db.session.rollback()
                flash('Error adding device. Please try again.', 'error')
                return redirect(url_for('add_server'))
        else:
            print("Form validation failed:", form.errors)
            flash('Form validation failed. Please check your inputs.', 'error')
    
    return render_template('add_server.html', form=form)

@app.route('/device/<int:device_id>', methods=['DELETE'])
@login_required
def delete_device(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        if device.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/notifications')
@login_required
def notifications():
    # Mock notifications data - you can replace this with actual notifications from your database
    notifications = [
        {"id": 1, "message": "Welcome to the dashboard!", "time": "Just now"},
        {"id": 2, "message": "New device added", "time": "2 hours ago"},
        {"id": 3, "message": "System update available", "time": "1 day ago"}
    ]
    return jsonify(notifications)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            # Set session as permanent but it will expire after PERMANENT_SESSION_LIFETIME
            session.permanent = True
            remember = 'remember' in request.form
            login_user(user, remember=remember)
            
            # Get the next page from the URL parameters, defaulting to dashboard
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
                
            flash('Logged in successfully.', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        if request.form.get('skip'):
            current_user.password_change_required = False
            db.session.commit()
            return redirect(url_for('dashboard'))
            
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('change_password'))
            
        current_user.set_password(new_password)
        current_user.password_change_required = False
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # Clear session
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/edit-device/<int:device_id>', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    
    # Check if user has permission to edit this device
    if not current_user.is_admin and device.user_id != current_user.id:
        flash('You do not have permission to edit this device.', 'error')
        return redirect(url_for('dashboard'))
    
    form = AddServerForm()
    
    if request.method == 'GET':
        # Pre-fill the form with device data
        form.server_name.data = device.name
        form.server_ip.data = device.ip_address
        form.server_type.data = device.device_type
        form.server_description.data = device.description
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            device.name = request.form['server-name']
            device.ip_address = request.form['server-ip']
            device.device_type = request.form['server-type']
            device.description = request.form['server-description']
            device.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Device updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            print("Error occurred:", str(e))
            db.session.rollback()
            flash('Error updating device. Please try again.', 'error')
    
    return render_template('edit_device.html', form=form, device=device)

# User Management Routes
@app.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    form = FlaskForm()  # Create a form instance for CSRF token
    return render_template('users.html', users=users, form=form)

@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('manage_users'))
    
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    flash('User added successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        return jsonify({'error': 'Cannot delete admin user'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/users/reset-password', methods=['POST'])
@login_required
def reset_user_password():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    user = User.query.get_or_404(user_id)
    user.set_password(new_password)
    db.session.commit()
    
    flash('Password reset successfully', 'success')
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
