from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_mail import Message
from app import db, mail
from models import Project, Skill, Experience, BlogPost, Testimonial, ContactMessage, SiteSettings
from forms import ContactForm
from utils import parse_tags, get_setting
from collections import defaultdict


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    featured_projects = Project.query.filter_by(is_featured=True).order_by(Project.order_index).limit(3).all()
    hero_title = get_setting('hero_title', 'Hi, I\'m Shawaiz')
    hero_subtitle = get_setting('hero_subtitle', 'I\'m a web developer and game builder.')

    # Group skills by category
    skills_by_category = defaultdict(list)
    all_skills = Skill.query.all()
    for skill in all_skills:
        skills_by_category[skill.category].append({
            'name': skill.name,
            'level': skill.level
        })

    return render_template('index.html', 
                           featured_projects=featured_projects,
                           hero_title=hero_title,
                           hero_subtitle=hero_subtitle,
                           skills_by_category=skills_by_category)
@bp.route('/about')
def about():
    experiences = Experience.query.order_by(Experience.order_index.desc()).all()
    about_text = get_setting('about_text', '')
    return render_template('about.html', experiences=experiences, about_text=about_text)

@bp.route('/projects')
def projects():
    category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Project.query
    if category != 'all':
        query = query.filter_by(category=category)
    
    projects = query.order_by(Project.order_index.desc(), Project.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )
    
    categories = db.session.query(Project.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('projects.html', 
                         projects=projects, 
                         categories=categories, 
                         current_category=category)

@bp.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

@bp.route('/skills')
def skills():
    skills_by_category = {}
    skills = Skill.query.order_by(Skill.category, Skill.order_index).all()
    
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    return render_template('skills.html', skills_by_category=skills_by_category)

@bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag')
    
    query = BlogPost.query.filter_by(is_published=True)
    if tag:
        query = query.filter(BlogPost.tags.like(f'%{tag}%'))
    
    posts = query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    # Get all tags
    all_posts = BlogPost.query.filter_by(is_published=True).all()
    all_tags = set()
    for post in all_posts:
        if post.tags:
            all_tags.update(parse_tags(post.tags))
    
    return render_template('blog.html', posts=posts, all_tags=sorted(all_tags), current_tag=tag)

@bp.route('/blog/<slug>')
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('blog_detail.html', post=post)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        # Save message to database
        message = ContactMessage()
        message.name = form.name.data
        message.email = form.email.data
        message.subject = form.subject.data
        message.message = form.message.data
        db.session.add(message)
        db.session.commit()
        
        # Send email notification (if configured)
        try:
            contact_email = get_setting('contact_email')
            if contact_email and mail.mail:
                msg = Message(
                    subject=f"Portfolio Contact: {form.subject.data or 'New Message'}",
                    recipients=[contact_email],
                    body=f"""
Name: {form.name.data}
Email: {form.email.data}
Subject: {form.subject.data}

Message:
{form.message.data}
                    """
                )
                mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        flash('Thank you for your message! I\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', form=form)
