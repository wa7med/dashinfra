from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import db, User, Device
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dashboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        db.drop_all()
        db.create_all()
        
        # Create default admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created!")

# Routes
@app.route('/')
@login_required
def dashboard():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', devices=devices)

@app.route('/add-server', methods=['GET', 'POST'])
@login_required
def add_server():
    if request.method == 'POST':
        new_device = Device(
            name=request.form['server-name'],
            ip_address=request.form['server-ip'],
            device_type=request.form['server-type'],
            description=request.form['server-description'],
            user_id=current_user.id
        )
        db.session.add(new_device)
        db.session.commit()
        flash('Device added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_server.html')

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
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
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
    return redirect(url_for('login'))

# User Management Routes
@app.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('users.html', users=users)

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
