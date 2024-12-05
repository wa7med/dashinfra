from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from models import db, User, Device, Activity
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from forms import UserForm  

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
            remember = request.form.get('remember', False)
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                log_activity(user, 'User logged in')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            
            flash('Invalid username or password')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        if current_user.is_authenticated:
            log_activity(current_user, 'User logged out')
        logout_user()
        session.clear()
        return redirect(url_for('login'))

    # User profile routes
    @app.route('/profile')
    @login_required
    def profile():
        activities = Activity.query.filter_by(user_id=current_user.id)\
                                 .order_by(Activity.timestamp.desc())\
                                 .limit(10).all()
        return render_template('profile.html', activities=activities)

    @app.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect')
            return redirect(url_for('profile'))

        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('profile'))

        current_user.set_password(new_password)
        db.session.commit()
        log_activity(current_user, 'Changed password')
        flash('Password updated successfully')
        return redirect(url_for('profile'))

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

    @app.route('/delete-device/<int:device_id>', methods=['POST'])
    @login_required
    def delete_device(device_id):
        device = Device.query.get_or_404(device_id)
        if not current_user.is_admin and device.user_id != current_user.id:
            flash('Unauthorized access')
            return redirect(url_for('dashboard'))
        
        device_name = device.name
        device_type = device.device_type
        db.session.delete(device)
        db.session.commit()
        log_activity(current_user, f'Deleted {device_type}: {device_name}')
        flash(f'{device_type.capitalize()} deleted successfully')
        return redirect(url_for('dashboard'))

    @app.route('/edit-device/<int:device_id>', methods=['GET', 'POST'])
    @login_required
    def edit_device(device_id):
        device = Device.query.get_or_404(device_id)
        if not current_user.is_admin and device.user_id != current_user.id:
            flash('Unauthorized access')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            device.name = request.form.get('name')
            device.ip_address = request.form.get('ip_address')
            device.username = request.form.get('username')
            device.description = request.form.get('description')
            
            new_password = request.form.get('password')
            if new_password:
                device.set_password(new_password)
            
            db.session.commit()
            log_activity(current_user, f'Updated {device.device_type}: {device.name}')
            flash(f'{device.device_type.capitalize()} updated successfully')
            return redirect(url_for('dashboard'))
        
        return render_template('edit_device.html', device=device)

    # User management routes (admin only)
    @app.route('/users')
    @login_required
    def users():
        if not current_user.is_admin:
            flash('Unauthorized access')
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
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'true'
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('users'))
        
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('users'))
            
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(current_user, f'Created new user: {username}')
        
        flash('User created successfully', 'success')
        return redirect(url_for('users'))

    @app.route('/delete-user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        log_activity(current_user, f'Deleted user: {username}')
        
        return jsonify({'message': 'User deleted successfully'})

    @app.route('/reset-user-password', methods=['POST'])
    @login_required
    def reset_user_password():
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password')
        
        user = User.query.get_or_404(user_id)
        user.set_password(new_password)
        db.session.commit()
        log_activity(current_user, f'Reset password for user: {user.username}')
        
        return jsonify({'message': 'Password reset successfully'})

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