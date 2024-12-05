from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from models import db, User, Device, Activity
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from forms import UserForm  
import re
from sqlalchemy.exc import SQLAlchemyError

class AddServerForm(FlaskForm):
    server_name = StringField('Server Name', validators=[DataRequired()], name='server-name')
    server_ip = StringField('Server IP', validators=[DataRequired()], name='server-ip')
    server_type = SelectField('Server Type', 
                            choices=[('server', 'Server'), 
                                   ('device', 'Device'), 
                                   ('camera', 'Camera')],
                            validators=[DataRequired()],
                            name='server-type')
    username = StringField('Username', name='username')
    password = PasswordField('Password', name='password')
    server_description = TextAreaField('Server Description', name='server-description')

def register_routes(app):
    def log_activity(user, action):
        activity = Activity(user_id=user.id, action=action, timestamp=datetime.utcnow())
        db.session.add(activity)
        db.session.commit()

    # Dashboard routes
    @app.route('/')
    @login_required
    def dashboard():
        page = request.args.get('page', 1, type=int)
        per_page = 10

        # Get total counts (not paginated)
        total_devices = Device.query.filter_by(device_type='server').count()
        total_active = Device.query.filter_by(status='active').count()
        total_cameras = Device.query.filter_by(device_type='camera').count()

        # Get paginated devices - show all devices to everyone
        devices_pagination = Device.query.paginate(page=page, per_page=per_page, error_out=False)
        devices = devices_pagination.items

        # Get usernames for all device owners
        user_ids = {device.user_id for device in devices_pagination.items}
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_dict = {user.id: user.username for user in users}
        
        return render_template('dashboard.html', 
                             devices=devices,
                             pagination=devices_pagination,
                             total_devices=total_devices,
                             total_active=total_active,
                             total_cameras=total_cameras,
                             user_dict=user_dict,
                             current_user=current_user)

    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                log_activity(user, 'User logged in')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            
            flash('Invalid username or password', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        if current_user.is_authenticated:
            log_activity(current_user, 'User logged out')
        logout_user()
        session.clear()
        flash('Successfully logged out', 'success')
        return redirect(url_for('login'))

    # User profile routes
    @app.route('/profile')
    @login_required
    def profile():
        activities = Activity.query.filter_by(user_id=current_user.id)\
                                 .order_by(Activity.timestamp.desc())\
                                 .limit(10).all()
        return render_template('profile.html', activities=activities)

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'GET':
            return render_template('change_password.html')
        
        try:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate inputs
            if not all([current_password, new_password, confirm_password]):
                flash('All fields are required', 'error')
                return redirect(url_for('change_password'))
            
            # Verify current password
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('change_password'))
            
            # Check new password length
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long', 'error')
                return redirect(url_for('change_password'))
            
            # Check if passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('change_password'))
            
            # Update password
            current_user.set_password(new_password)
            db.session.commit()
            
            # Log activity
            log_activity(current_user, 'Changed password')
            flash('Password changed successfully', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            app.logger.error(f'Error in change_password: {str(e)}')
            return redirect(url_for('change_password'))

    # Device management routes
    @app.route('/add-server', methods=['GET', 'POST'])
    @login_required
    def add_server():
        form = AddServerForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    device = Device(
                        name=form.server_name.data,
                        ip_address=form.server_ip.data,
                        device_type=form.server_type.data,
                        username=form.username.data,
                        password=form.password.data,
                        description=form.server_description.data,
                        user_id=current_user.id,
                        status='active'
                    )
                    db.session.add(device)
                    db.session.commit()
                    log_activity(current_user, f'Added new device: {device.name}')
                    flash('Device added successfully', 'success')
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding device: {str(e)}', 'error')
                    return render_template('add_server.html', form=form)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'error')
                return render_template('add_server.html', form=form)
        return render_template('add_server.html', form=form)

    @app.route('/edit-device/<int:device_id>', methods=['GET', 'POST'])
    @login_required
    def edit_device(device_id):
        device = Device.query.get_or_404(device_id)
        
        if request.method == 'POST':
            try:
                device.name = request.form.get('name')
                device.ip_address = request.form.get('ip_address')
                device.username = request.form.get('username')
                password = request.form.get('password')
                if password:  # Only update password if provided
                    device.password = password
                device.description = request.form.get('description')
                
                db.session.commit()
                log_activity(current_user, f'Updated device {device.name}')
                flash('Device updated successfully', 'success')
                return redirect(url_for('dashboard'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Error updating device. Please try again.', 'error')
                app.logger.error(f'Error updating device: {str(e)}')
        
        return render_template('edit_device.html', device=device)

    @app.route('/delete-device/<int:device_id>', methods=['POST'])
    @login_required
    def delete_device(device_id):
        try:
            device = Device.query.get_or_404(device_id)
            device_name = device.name
            db.session.delete(device)
            db.session.commit()
            log_activity(current_user, f'Deleted device {device_name}')
            return jsonify({
                'message': 'Device deleted successfully',
                'redirect': url_for('dashboard')
            })
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Error deleting device: {str(e)}')
            return jsonify({'error': 'Error deleting device'}), 500

    # User management routes (admin only)
    @app.route('/users')
    @login_required
    def users():
        if not current_user.is_admin:
            flash('Unauthorized access', 'error')
            return redirect(url_for('dashboard'))
        
        users = User.query.all()
        form = UserForm()  
        return render_template('users.html', users=users, form=form)

    @app.route('/add-user', methods=['POST'])
    @login_required
    def add_user():
        if not current_user.is_admin:
            flash('Unauthorized access', 'error')
            return redirect(url_for('users'))
        
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password')
            is_admin = request.form.get('is_admin') == 'true'
            
            # Validate required fields
            if not all([username, email, password]):
                flash('All fields are required', 'error')
                return redirect(url_for('users'))
            
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email format', 'error')
                return redirect(url_for('users'))
            
            # Check username length
            if len(username) < 3:
                flash('Username must be at least 3 characters long', 'error')
                return redirect(url_for('users'))
            
            # Check password length
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('users'))
            
            # Check for existing username
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('users'))
            
            # Check for existing email
            if User.query.filter_by(email=email).first():
                flash('Email address already exists', 'error')
                return redirect(url_for('users'))
            
            # Create new user
            user = User(username=username, email=email, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Log activity and show success message
            log_activity(current_user, f'Created new user: {username}')
            flash('User created successfully', 'success')
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')
            app.logger.error(f'Database error in add_user: {str(e)}')
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred', 'error')
            app.logger.error(f'Unexpected error in add_user: {str(e)}')
        
        return redirect(url_for('users'))

    @app.route('/delete-user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            user = User.query.get_or_404(user_id)
            
            # Prevent self-deletion
            if user.id == current_user.id:
                return jsonify({'error': 'Cannot delete your own account'}), 400
            
            # Prevent deletion of super admin
            if user.username == 'admin':
                return jsonify({'error': 'Cannot delete super admin account'}), 400
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            log_activity(current_user, f'Deleted user: {username}')
            return jsonify({'message': 'User deleted successfully'})
            
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Database error in delete_user: {str(e)}')
            return jsonify({'error': 'Database error occurred'}), 500
        except Exception as e:
            app.logger.error(f'Unexpected error in delete_user: {str(e)}')
            return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.route('/reset-user-password', methods=['GET', 'POST'])
    @login_required
    def reset_user_password():
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            user_id = request.form.get('user_id')
            new_password = request.form.get('new_password')
            
            # Validate inputs
            if not all([user_id, new_password]):
                flash('Password is required', 'error')
                return redirect(url_for('users'))
            
            # Validate password length
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('users'))
            
            # Get user and validate
            user = User.query.get_or_404(user_id)
            
            # Prevent resetting admin password if not admin
            if user.username == 'admin' and current_user.username != 'admin':
                flash('Cannot reset admin password', 'error')
                return redirect(url_for('users'))
            
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            # Log activity
            log_activity(current_user, f'Reset password for user: {user.username}')
            flash('Password reset successfully', 'success')
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')
            app.logger.error(f'Database error in reset_user_password: {str(e)}')
        except Exception as e:
            flash('An unexpected error occurred', 'error')
            app.logger.error(f'Unexpected error in reset_user_password: {str(e)}')
        
        return redirect(url_for('users'))

    # Activity monitoring routes
    @app.route('/activity-history')
    @login_required
    def activity_history():
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        if current_user.is_admin:
            activities = Activity.query
        else:
            activities = Activity.query.filter_by(user_id=current_user.id)
        
        activities = activities.order_by(Activity.timestamp.desc())\
                             .paginate(page=page, per_page=per_page)
        
        return render_template('activity_history.html', activities=activities)

    @app.route('/notifications')
    @login_required
    def notifications():
        # Get recent activities for the user's devices
        if current_user.is_admin:
            activities = Activity.query.order_by(Activity.timestamp.desc()).limit(10).all()
        else:
            activities = Activity.query.filter_by(user_id=current_user.id)\
                                     .order_by(Activity.timestamp.desc())\
                                     .limit(10).all()
        return jsonify([{
            'action': activity.action,
            'timestamp': activity.timestamp.isoformat()
        } for activity in activities])

    # Health check endpoints
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'db': check_db_connection(),
            'redis': check_redis_connection()
        })

    @app.route('/health/db')
    def db_health():
        is_healthy = check_db_connection()
        return jsonify({'status': 'healthy' if is_healthy else 'unhealthy'})

    @app.route('/health/redis')
    def redis_health():
        is_healthy = check_redis_connection()
        return jsonify({'status': 'healthy' if is_healthy else 'unhealthy'})

    def check_db_connection():
        try:
            db.session.execute('SELECT 1')
            return True
        except Exception as e:
            app.logger.error(f"Database connection error: {str(e)}")
            return False

    def check_redis_connection():
        try:
            app.extensions['cache'].get('health_check')
            return True
        except Exception as e:
            app.logger.error(f"Redis connection error: {str(e)}")
            return False

    return app