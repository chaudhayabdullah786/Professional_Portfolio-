from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import (AdminUser, Project, Skill, Experience, Certificate, BlogPost, 
                   Testimonial, ContactMessage, SiteSettings)
from forms import (LoginForm, ProjectForm, SkillForm, ExperienceForm, BlogPostForm, 
                  TestimonialForm, SettingsForm)
from utils import save_uploaded_file, create_slug, set_setting, get_setting
import os

bp = Blueprint('admin', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            user = AdminUser.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
        else:
            flash('Please enter both username and password.', 'danger')
    
    form = LoginForm()
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/')
@login_required
def dashboard():
    stats = {
        'projects': Project.query.count(),
        'blog_posts': BlogPost.query.count(),
        'messages': ContactMessage.query.filter_by(is_read=False).count(),
        'skills': Skill.query.count(),
    }
    
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_messages=recent_messages)

# Project Management
@bp.route('/projects')
@login_required
def projects():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.order_index.desc(), Project.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/projects.html', projects=projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project()
        project.title = form.title.data
        project.short_description = form.short_description.data
        project.description = form.description.data
        project.category = form.category.data
        project.tech_stack = form.tech_stack.data
        project.tags = form.tags.data
        project.github_link = form.github_link.data
        project.live_link = form.live_link.data
        project.is_featured = form.is_featured.data
        project.order_index = form.order_index.data
        
        if form.image.data:
            static_folder = current_app.static_folder or 'static'
            filename = save_uploaded_file(
                form.image.data, 
                os.path.join(static_folder, 'uploads', 'projects'),
                max_size=(800, 600)
            )
            if filename:
                project.image_path = f'uploads/projects/{filename}'
        
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, title='New Project')

@bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        form.populate_obj(project)
        
        if form.image.data:
            static_folder = current_app.static_folder or 'static'
            filename = save_uploaded_file(
                form.image.data, 
                os.path.join(static_folder, 'uploads', 'projects'),
                max_size=(800, 600)
            )
            if filename:
                project.image_path = f'uploads/projects/{filename}'
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, project=project, title='Edit Project')

@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin.projects'))

# Blog Management
@bp.route('/blog')
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/blog.html', posts=posts)

@bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        slug = form.slug.data or create_slug(form.title.data)
        
        post = BlogPost()
        post.title = form.title.data
        post.slug = slug
        post.excerpt = form.excerpt.data
        post.content = form.content.data
        post.tags = form.tags.data
        post.is_published = form.is_published.data
        
        if form.image.data:
            static_folder = current_app.static_folder or 'static'
            filename = save_uploaded_file(
                form.image.data, 
                os.path.join(static_folder, 'uploads', 'blog'),
                max_size=(800, 400)
            )
            if filename:
                post.image_path = f'uploads/blog/{filename}'
        
        db.session.add(post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/blog_form.html', form=form, title='New Blog Post')

@bp.route('/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog_post(id):
    post = BlogPost.query.get_or_404(id)
    form = BlogPostForm(obj=post)
    
    if form.validate_on_submit():
        form.populate_obj(post)
        
        if form.image.data:
            static_folder = current_app.static_folder or 'static'
            filename = save_uploaded_file(
                form.image.data, 
                os.path.join(static_folder, 'uploads', 'blog'),
                max_size=(800, 400)
            )
            if filename:
                post.image_path = f'uploads/blog/{filename}'
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/blog_form.html', form=form, post=post, title='Edit Blog Post')

@bp.route('/blog/<int:id>/delete', methods=['POST'])
@login_required
def delete_blog_post(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.blog'))

# Skills Management
@bp.route('/skills')
@login_required
def skills():
    skills = Skill.query.order_by(Skill.category, Skill.order_index).all()
    return render_template('admin/skills.html', skills=skills)

@bp.route('/skills/new', methods=['GET', 'POST'])
@login_required
def new_skill():
    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill()
        skill.name = form.name.data
        skill.category = form.category.data
        skill.level = form.level.data
        skill.order_index = form.order_index.data
        db.session.add(skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
        return redirect(url_for('admin.skills'))
    
    return render_template('admin/skill_form.html', form=form, title='New Skill')

@bp.route('/skills/<int:id>/delete', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('admin.skills'))

from flask import flash, redirect, url_for
from flask_login import login_required
from models import Experience


# Experience Management
@bp.route('/experience')
@login_required
def experience():
    experiences = Experience.query.order_by(Experience.order_index.desc()).all()
    return render_template('admin/experience.html', experiences=experiences)

@bp.route('/experience/new', methods=['GET', 'POST'])
@login_required
def new_experience():
    form = ExperienceForm()
    if form.validate_on_submit():
        experience = Experience()
        experience.job_title = form.job_title.data
        experience.company = form.company.data
        experience.location = form.location.data
        experience.start_date = form.start_date.data
        experience.end_date = form.end_date.data
        experience.description = form.description.data
        experience.is_current = form.is_current.data
        experience.order_index = form.order_index.data
        db.session.add(experience)
        db.session.commit()
        flash('Experience added successfully!', 'success')
        return redirect(url_for('admin.experience'))
    
    return render_template('admin/experience_form.html', form=form, title='New Experience')


@bp.route('/admin/experience/delete/<int:id>', methods=['POST'])
@login_required
def delete_experience(id):
    experience = Experience.query.get_or_404(id)
    db.session.delete(experience)
    db.session.commit()
    flash('Experience deleted successfully.', 'success')
    return redirect(url_for('admin.experience'))



# Messages Management
@bp.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/messages.html', messages=messages)

@bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def mark_message_read(id):
    message = ContactMessage.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    return redirect(url_for('admin.messages'))

@bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin.messages'))

# Admin Management
@bp.route('/admins')
@login_required
def admins():
    admin_users = AdminUser.query.order_by(AdminUser.created_at.desc()).all()
    return render_template('admin/admins.html', admin_users=admin_users)

@bp.route('/admins/new', methods=['GET', 'POST'])
@login_required
def new_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username and email and password:
            # Check if username or email already exists
            existing_user = AdminUser.query.filter(
                (AdminUser.username == username) | (AdminUser.email == email)
            ).first()
            
            if existing_user:
                flash('Username or email already exists!', 'danger')
            else:
                admin_user = AdminUser()
                admin_user.username = username
                admin_user.email = email
                admin_user.password_hash = generate_password_hash(password)
                db.session.add(admin_user)
                db.session.commit()
                flash('Admin user created successfully!', 'success')
                return redirect(url_for('admin.admins'))
        else:
            flash('Please fill in all fields.', 'danger')
    
    return render_template('admin/admin_form.html', title='New Admin')

@bp.route('/admins/<int:id>/delete', methods=['POST'])
@login_required
def delete_admin(id):
    if id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.admins'))
    
    admin_user = AdminUser.query.get_or_404(id)
    db.session.delete(admin_user)
    db.session.commit()
    flash('Admin user deleted successfully!', 'success')
    return redirect(url_for('admin.admins'))

# Settings
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    
    if request.method == 'GET':
        # Populate form with current settings
        form.site_title.data = get_setting('site_title', 'Portfolio')
        form.site_description.data = get_setting('site_description', '')
        form.hero_title.data = get_setting('hero_title', 'Hi, I\'m Shawaiz')
        form.hero_subtitle.data = get_setting('hero_subtitle', 'I\'m a web developer and game builder.')
        form.about_text.data = get_setting('about_text', '')
        form.contact_email.data = get_setting('contact_email', '')
        form.github_url.data = get_setting('github_url', '')
        form.linkedin_url.data = get_setting('linkedin_url', '')
        form.twitter_url.data = get_setting('twitter_url', '')
    
    if form.validate_on_submit():
        # Save all settings
        set_setting('site_title', form.site_title.data)
        set_setting('site_description', form.site_description.data)
        set_setting('hero_title', form.hero_title.data)
        set_setting('hero_subtitle', form.hero_subtitle.data)
        set_setting('about_text', form.about_text.data)
        set_setting('contact_email', form.contact_email.data)
        set_setting('github_url', form.github_url.data)
        set_setting('linkedin_url', form.linkedin_url.data)
        set_setting('twitter_url', form.twitter_url.data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)
