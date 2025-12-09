# Overview

This is a fully functional Flask-based portfolio website for Shawaiz, a web developer and game builder. The application features a complete public-facing portfolio with sections for projects, skills, experience, blog posts, and contact functionality, alongside a comprehensive admin panel for content management. The site is designed to showcase professional work while providing an easy-to-use content management system.

## Project Status: ✅ COMPLETED (December 2024)
- All features implemented and working
- Database models created and functioning
- Admin panel fully operational (admin/admin123)
- All template errors resolved
- Application successfully deployed and running

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **UI Framework**: Bootstrap 5.3.0 with Font Awesome icons and Google Fonts (Inter)
- **Client-side Enhancement**: Custom JavaScript for smooth scrolling, navbar effects, skill bar animations, and form interactions
- **Rich Text Editing**: CKEditor integration for blog content and project descriptions
- **Responsive Design**: Mobile-first approach with CSS custom properties for theming

## Backend Architecture
- **Web Framework**: Flask with blueprint-based route organization
- **Authentication**: Flask-Login for admin session management with secure password hashing
- **Form Handling**: Flask-WTF with comprehensive form validation and CSRF protection
- **File Management**: Custom utility functions for secure file uploads with image resizing using Pillow
- **Email Integration**: Flask-Mail for contact form submissions and notifications

## Data Layer
- **ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **Database Models**: Comprehensive models for AdminUser, Project, Skill, Experience, Certificate, BlogPost, Testimonial, ContactMessage, and SiteSettings
- **Database Configuration**: Configurable database URL with connection pooling and health checks
- **Schema Design**: Relational structure with proper indexing and timestamp tracking

## Content Management
- **Admin Panel**: Complete CRUD operations for all content types
- **Dynamic Settings**: Site-wide configuration through database-stored settings
- **Media Upload**: Secure file upload system with image optimization
- **Rich Content**: CKEditor integration for formatted content creation
- **SEO Features**: URL slug generation and meta tag management

## Security Implementation
- **Authentication**: Secure login system with password hashing using Werkzeug
- **Session Management**: Flask-Login with secure session configuration
- **File Upload Security**: Whitelist-based file type validation and secure filename handling
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Environment Configuration**: Secure credential management through environment variables

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework with SQLAlchemy, Login, and Mail extensions
- **Bootstrap 5.3.0**: Frontend CSS framework via CDN
- **Font Awesome 6.4.0**: Icon library via CDN
- **Google Fonts**: Inter font family for typography

## Database & ORM
- **SQLAlchemy**: Database ORM with declarative base configuration
- **Flask-SQLAlchemy**: Flask integration with connection pooling
- **Database**: Configurable (defaults to SQLite for development, supports PostgreSQL via DATABASE_URL)

## Rich Text & Media
- **CKEditor 4.22.1**: WYSIWYG editor for content creation via CDN
- **Pillow (PIL)**: Image processing for upload optimization and resizing
- **Werkzeug**: Secure filename handling and file utilities

## Email & Communication
- **Flask-Mail**: Email functionality for contact forms
- **SMTP Configuration**: Gmail SMTP support with TLS encryption
- **Environment-based Email Settings**: Configurable mail server credentials

## Deployment & Production
- **ProxyFix Middleware**: Support for reverse proxy deployments
- **Environment Variables**: Configuration management for production secrets
- **File Upload Limits**: Configurable maximum file sizes (16MB default)
- **Static File Serving**: Organized asset structure for CSS, JavaScript, and uploads




## How to run Local

-> pip install -r requirements.txt
(if any error about about installing tha library occur then install that library)
like
pip install (library name)

-> python main.py 
