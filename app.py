from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db, Category, Topics , User
import uuid
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session.permanent = True
            try:
                user.last_login = datetime.utcnow()
                db.session.commit()
            except:
                pass
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def dashboard():
    from datetime import datetime
    
    categories = Category.query.all()
    category_count = len(categories)
    topics = Topics.query.all()
    topic_count = len(topics)
    published_topics = Topics.query.filter_by(published=True).all()
    published_count = len(published_topics)
    draft_topics = Topics.query.filter_by(published=False).all()
    draft_count = len(draft_topics)
    
    # Calculate topics created this month
    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year
    topics_this_month = Topics.query.filter(
        db.extract('month', Topics.created_at) == current_month,
        db.extract('year', Topics.created_at) == current_year
    ).all()
    topics_this_month_count = len(topics_this_month)
    
    # Calculate topics published this month
    published_this_month = Topics.query.filter(
        Topics.published == True,
        db.extract('month', Topics.created_at) == current_month,
        db.extract('year', Topics.created_at) == current_year
    ).all()
    published_this_month_count = len(published_this_month)
    
    # Get recent topics (last 5)
    recent_topics = Topics.query.order_by(Topics.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', categories=categories, category_count=category_count, topics=topics, topic_count=topic_count, published_count=published_count, draft_count=draft_count, topics_this_month_count=topics_this_month_count, published_this_month_count=published_this_month_count, recent_topics=recent_topics)

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        
        if name:
            if not slug:
                slug = name.lower().replace(' ', '-').replace('/', '-')
            
            new_category = Category(name=name, slug=slug, description=description)
            db.session.add(new_category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('categories'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories, category_count=len(categories))

@app.route('/admin/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories'))

@app.route('/admin/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        category.description = request.form.get('description')
        
        if not category.slug:
            category.slug = category.name.lower().replace(' ', '-').replace('/', '-')
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories, category_count=len(categories), edit_category=category)

@app.route('/admin/topics', methods=['GET', 'POST'])
@login_required
def topics():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        body = request.form.get('body')
        scripture_ref = request.form.get('scripture_ref_hidden')
        published = request.form.get('published') == 'on'
        
        # Handle thumbnail upload
        thumbnail = None
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename:
                from werkzeug.utils import secure_filename
                import os
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join('static', 'uploads')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                # Save file with unique name
                import uuid
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                thumbnail = '/static/uploads/' + unique_filename
        
        if title and category_id:
            if not slug:
                slug = title.lower().replace(' ', '-').replace('/', '-')
            
            new_topic = Topics(
                title=title, 
                slug=slug, 
                category_id=category_id,
                description=description,
                body=body,
                scripture_ref=scripture_ref,
                thumbnail=thumbnail,
                published=published
            )
            db.session.add(new_topic)
            db.session.commit()
            flash('Topic created successfully!', 'success')
            return redirect(url_for('topics'))
    
    topics = Topics.query.all()
    categories = Category.query.all()
    return render_template('admin/topics.html', topics=topics, categories=categories, topic_count=len(topics))

@app.route('/admin/topics/<int:id>/delete', methods=['POST'])
@login_required
def delete_topic(id):
    topic = Topics.query.get_or_404(id)
    db.session.delete(topic)
    db.session.commit()
    flash('Topic deleted successfully!', 'success')
    return redirect(url_for('topics'))

@app.route('/admin/topics/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(id):
    topic = Topics.query.get_or_404(id)
    
    if request.method == 'POST':
        topic.title = request.form.get('title')
        topic.slug = request.form.get('slug')
        topic.category_id = request.form.get('category_id')
        topic.description = request.form.get('description')
        topic.body = request.form.get('body')
        topic.scripture_ref = request.form.get('scripture_ref_hidden')
        topic.published = request.form.get('published') == 'on'
        
        # Handle thumbnail upload
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename:
                from werkzeug.utils import secure_filename
                import os
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join('static', 'uploads')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                # Save file with unique name
                import uuid
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                topic.thumbnail = '/static/uploads/' + unique_filename
        
        if not topic.slug:
            topic.slug = topic.title.lower().replace(' ', '-').replace('/', '-')
        
        db.session.commit()
        flash('Topic updated successfully!', 'success')
        return redirect(url_for('topics'))
    
    topics = Topics.query.all()
    categories = Category.query.all()
    return render_template('admin/topics.html', topics=topics, categories=categories, topic_count=len(topics), edit_topic=topic)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def users():
    if not current_user.is_super_admin:
        flash('Access denied. Only super admin can manage users.', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == 'on'
        is_super_admin = request.form.get('is_super_admin') == 'on'
        photo = request.files.get('photo')
        
        if name and email and password:
            hashed_password = generate_password_hash(password)
            
            # Handle photo upload
            photo_filename = None
            if photo and photo.filename:
                photo_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                upload_folder = os.path.join('static', 'uploads', 'users')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                photo_path = os.path.join(upload_folder, photo_filename)
                photo.save(photo_path)
            
            new_user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                photo=photo_filename,
                role=role,
                is_super_admin=is_super_admin,
                is_active=is_active
            )
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('users'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_super_admin:
        flash('Access denied. Only super admin can manage users.', 'error')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users'))

@app.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    is_own_profile = (id == current_user.id)
    
    # Only super admin can edit other users' profiles
    if not is_own_profile and not current_user.is_super_admin:
        flash('Access denied. Only super admin can manage other users.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        old_email = user.email
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        password = request.form.get('password')
        
        # Only super admin can change role, active status, and super admin status for OTHER users
        # When editing own profile, these fields are hidden in the form
        if current_user.is_super_admin and not is_own_profile:
            user.role = request.form.get('role')
            user.is_active = request.form.get('is_active') == 'on'
            user.is_super_admin = request.form.get('is_super_admin') == 'on'
        
        if password:
            user.password_hash = generate_password_hash(password)
        
        # Handle photo upload
        photo = request.files.get('photo')
        if photo and photo.filename:
            # Delete old photo if exists
            if user.photo:
                old_photo_path = os.path.join('static', 'uploads', 'users', user.photo)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            
            photo_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
            upload_folder = os.path.join('static', 'uploads', 'users')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            photo_path = os.path.join(upload_folder, photo_filename)
            photo.save(photo_path)
            user.photo = photo_filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # If user changed their own email, logout and force re-login
        if is_own_profile and old_email != user.email:
            logout_user()
            flash('Email changed. Please log in with your new email.', 'info')
            return redirect(url_for('login'))
        
        # Redirect to profile page if editing own profile, otherwise to users page
        if is_own_profile:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('users'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users, edit_user=user, is_own_profile=is_own_profile)

@app.route('/admin/settings')
@login_required
def settings():
    return render_template('admin/settings.html')

@app.route('/admin/profile')
@login_required
def profile():
    return render_template('admin/profile.html')

def create_default_admin():
    admin = User.query.filter_by(email='admin@truedisciple.rw').first()
    if not admin:
        hashed_password = generate_password_hash('admin@herbez#7')
        admin = User(
            name='Admin',
            email='admin@truedisciple.rw',
            password_hash=hashed_password,
            is_super_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Default admin user created: admin@truedisciple.rw')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    app.run(debug=True)
