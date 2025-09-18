from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "careerpath_secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# -------------------------------
# Database Models
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/guidance")
def guidance():
    return render_template("guidance.html")

@app.route('/about')
def about():
    return render_template('about.html')
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")
@app.route('/resume-builder')
def resume_builder():
    return render_template('resume_builder.html')


@app.route("/pathfinder", methods=["GET", "POST"])
def pathfinder():
    recommendation = None
    resources = []

    if request.method == "POST":
        courses = int(request.form["courses"])
        internships = int(request.form["internships"])
        field = request.form["field"]
        skills = request.form["skills"].lower()

        # Basic logic for career recommendation
        if field == "Software Development":
            if "python" in skills or "java" in skills:
                recommendation = "Software Engineer / Full Stack Developer"
                resources = ["FreeCodeCamp - Web Dev", "Coursera - Java Programming", "Internshala - Software Internships"]
            else:
                recommendation = "Improve coding skills to aim for Software Development roles."
                resources = ["W3Schools - Programming Basics", "HackerRank Practice"]

        elif field == "Data Science":
            if courses >= 3 and ("python" in skills or "sql" in skills):
                recommendation = "Data Scientist / Data Analyst"
                resources = ["Kaggle Datasets", "Google Data Analytics Certificate", "NPTEL - Data Science Course"]
            else:
                recommendation = "Start with foundational Data Science courses."
                resources = ["Khan Academy - Statistics", "Coursera - Data Science Basics"]

        elif field == "Healthcare":
            recommendation = "Healthcare Professional (Nurse, Medical Assistant, Doctor)"
            resources = ["WHO Free Courses", "NPTEL - Healthcare Management", "Internships at Local Hospitals"]

        elif field == "Design":
            if "photoshop" in skills or "figma" in skills:
                recommendation = "UI/UX Designer or Graphic Designer"
                resources = ["Canva Free Courses", "Coursera UI/UX Specialization", "Skillshare - Graphic Design"]
            else:
                recommendation = "Build creative software skills for design careers."
                resources = ["YouTube - Photoshop Tutorials", "FreeCodeCamp UI/UX Guide"]

        elif field == "Finance":
            recommendation = "Accountant / Investment Banker / Financial Analyst"
            resources = ["Coursera Finance Basics", "NSE India Free Courses", "Internships with Banks"]

        elif field == "Marketing":
            recommendation = "Digital Marketer / SEO Specialist / Social Media Manager"
            resources = ["Google Digital Garage", "HubSpot Academy Free Marketing Courses", "Internshala - Marketing Internships"]

        elif field == "Engineering":
            recommendation = "Mechanical / Civil / Electrical Engineer"
            resources = ["NPTEL Engineering Courses", "MIT OpenCourseWare", "Internships at Core Companies"]

        # Extra encouragement
        if internships == 0:
            resources.append("Try doing internships on Internshala or LinkedIn to gain practical exposure.")

    return render_template("pathfinder.html", recommendation=recommendation, resources=resources)

@app.route('/careers')
def careers():
    careers_list = Career.query.all()
    return render_template('careers.html', careers=careers_list)

@app.route('/roadmap/<int:career_id>')
def roadmap(career_id):
    career = Career.query.get_or_404(career_id)
    return render_template('roadmap.html', career=career)

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/internships')
def internships():
    return render_template('internships.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# -------------------------------
# Authentication
# -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid credentials. Try again.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))

# -------------------------------
# Initialize DB
# -------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
