# M. Abdullah — Portfolio Website

A personal portfolio and content-management site built with Flask — featuring a public portfolio, project listings, skills, experience, blog posts, and a full admin panel for easy content management.

## 🚀 Live Demo  
(https://mabdullahdataanalyst786.pythonanywhere.com/)

---

## 🧩 Table of Contents  
- [About The Project](#about-the-project)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Prerequisites](#prerequisites)  
- [Installation & Setup (Local)](#installation--setup-local)  
- [Usage](#usage)  
- [Admin Credentials (for testing)](#admin-credentials-for-testing)  
- [Folder / Project Structure Overview](#folder--project-structure-overview)  
- [Deployment / Production Notes](#deployment--production-notes)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  
- [Acknowledgments](#acknowledgments)  

---

## About The Project

This repository contains a complete Flask-based personal portfolio website for **M. Abdullah**, showcasing professional work, development skills, and projects.  
It includes a full **admin dashboard (CMS)** that allows easy creation and management of:

- Projects  
- Blog posts  
- Skills  
- Experience sections  
- Testimonials  
- Certificates  
- Site-wide settings  

The system is designed for both professional presentation and effortless content updates.

---

## Features

- ✔️ Public portfolio (projects, skills, blog, experience, testimonials, contact form)  
- ✔️ Full CMS with CRUD operations for all content  
- ✔️ Secure admin login with password hashing  
- ✔️ Rich-text editor (CKEditor) for blog and project descriptions  
- ✔️ Secure image uploads with resizing (Pillow)  
- ✔️ Mobile-first responsive UI using Bootstrap 5  
- ✔️ SEO-friendly URLs and slug generation  
- ✔️ Email system using Flask-Mail (contact form notifications)  
- ✔️ Built-in CSRF protection for all forms  
- ✔️ SQLite for development, PostgreSQL supported for production  

---

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Mail  
- **Frontend:** Jinja2, Bootstrap 5, Font Awesome, Google Fonts (Inter), Vanilla JS  
- **Media & Rich Content:** CKEditor, Pillow  
- **Database:** SQLite (default) or PostgreSQL (via `DATABASE_URL`)  
- **Deployment:** Vercel / Custom server + ProxyFix + environment configs  

---

## Prerequisites

- Python 3.x  
- pip  
- (Optional) PostgreSQL for production  
- Environment variables for:  
  - SECRET_KEY  
  - MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT  
  - DATABASE_URL (if PostgreSQL is used)  

---

## Installation & Setup (Local)

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt

# Environment variables:
export SECRET_KEY="your-secret-key"
export FLASK_APP=main.py
export MAIL_USERNAME="your-email"
export MAIL_PASSWORD="your-password"

# (Optional) PostgreSQL:
export DATABASE_URL="postgresql://user:pass@host/dbname"

python main.py
# or:
flask run
