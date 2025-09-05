📂 Career Path Navigator

Career Path Navigator is a web-based platform designed to help students and beginners explore career opportunities, discover skill-building courses, and find relevant internships. The platform is built using Flask, SQLite, and Bootstrap, making it lightweight, responsive, and easy to deploy.

Features

User Registration & Login – Secure login and personalized profile.

Explore Careers – Browse multiple career options with short descriptions.

Career Roadmap – Step-by-step roadmap for each career, including skill development guidance.

Courses & Certifications – Links to free and paid courses (Coursera, Udemy, NPTEL, Skill India).

Internship Opportunities – Links to internships on Internshala, LinkedIn, and AngelList.

Responsive Design – Bootstrap-based UI compatible with desktop and mobile devices.

Folder Structure
career-path-navigator/
│
├── app.py                 # Main Flask application
├── speed.py               # Alternate name for Flask app (if used)
├── requirements.txt       # All Python dependencies
├── seed.py                # Script to populate sample careers in DB
├── static/
│   └── css/
│       └── style.css      # Custom styling for UI
├── templates/
│   ├── base.html          # Base template with navbar/footer
│   ├── index.html         # Home page
│   ├── careers.html       # List of career options
│   ├── roadmap.html       # Career roadmap details
│   ├── courses.html       # Learning resources
│   ├── internships.html   # Internship listings
│   ├── about.html         # About project
│   ├── register.html      # User signup
│   ├── login.html         # User login
│   └── profile.html       # User dashboard/profile
└── career_path_navigator.db # SQLite database (created after running)

Installation

Clone the repository

git clone https://github.com/YOUR_GITHUB_USERNAME/career-path-navigator.git
cd career-path-navigator


Create a virtual environment

python -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows


Install dependencies

pip install -r requirements.txt


Initialize the database

python
>>> from speed import db
>>> db.create_all()
>>> exit()


Seed sample data (optional)

python seed.py

Running the Application
Local Development
export FLASK_APP=speed.py       # Linux/Mac
set FLASK_APP=speed.py          # Windows

export FLASK_ENV=development    # Linux/Mac
set FLASK_ENV=development       # Windows

flask run


Visit http://127.0.0.1:5000
 in your browser.

Deployment

Use Render or Cloudflare Tunnel to make a public link.

Start Command (Render):

gunicorn speed:app


Build Command (Render):

pip install -r requirements.txt

Environment Variables (Optional)

SECRET_KEY → Used for Flask session security

FLASK_ENV → Set to production or development

Example in speed.py:

import os
app.secret_key = os.environ.get("SECRET_KEY", "mydefaultsecret")

Contributing

Fork the repository

Create a new branch (git checkout -b feature-name)

Make your changes

Commit (git commit -m "Add new feature")

Push (git push origin feature-name)

Open a Pull Request

License

This project is licensed under the MIT License