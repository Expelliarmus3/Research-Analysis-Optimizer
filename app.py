import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from models import db, User, Internship, Application

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsync-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devsync.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTH ROUTES ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'Professor':
            return redirect('/professor')
        return redirect('/student')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.form.get('email')).first()
    if user and user.password == request.form.get('password'):
        login_user(user)
        if user.role == 'Professor':
            return redirect('/professor')
        return redirect('/student')
    return "Invalid Credentials"

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    if User.query.filter_by(email=email).first(): return "Email exists"
    
    # User selects role in signup form
    role = request.form.get('role') 
    new_user = User(email=email, password=request.form.get('password'), role=role, full_name=request.form.get('full_name'))
    
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect('/setup')

@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.qualification = request.form.get('qualification')
        current_user.college = request.form.get('college')
        current_user.phone = request.form.get('phone')
        db.session.commit()
        if current_user.role == 'Professor':
            return redirect('/professor')
        return redirect('/student')
    return render_template('setup.html')

# --- STUDENT ROUTES ---

@app.route('/student')
@login_required
def student():
    if current_user.role == 'Professor': return redirect('/professor')
    return render_template('student.html')

@app.route('/papers')
@login_required
def papers():
    internships = Internship.query.all()
    return render_template('papers.html', internships=internships)

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

# FILE: app.py (Replace just the optimize route)

@app.route('/optimize', methods=['POST'])
@login_required
def optimize():
    data = request.json
    url = data.get('url', '').lower()
    
    # 1. SMART SIMULATION DATA
    # Default (CS/AI)
    analysis_data = {
        "summary": "This paper introduces a novel architecture for temporal forecasting using Gated Recurrent Units (TGRUs). It outperforms LSTM benchmarks by 15% on meteorological datasets.",
        "skills": ["Python", "TensorFlow", "Time-Series Analysis", "Calculus"],
        "citation_score": "520 (Top 5% Impact)",
        "professor": "Dr. Elara Vance",
        "vacancies": "2 Research Interns",
        "applicants": 12
    }

    # Custom Domains
    if any(x in url for x in ['bio', 'med', 'health', 'gene']):
        analysis_data.update({
            "summary": "This study explores CRISPR-Cas9 gene editing techniques for treating hereditary blood disorders.",
            "skills": ["Bioinformatics", "Genetics", "Lab Safety"],
            "professor": "Dr. Sarah Chen",
            "vacancies": "1 Lab Assistant"
        })
    elif any(x in url for x in ['energy', 'solar', 'climate']):
        analysis_data.update({
            "summary": "This paper investigates Perovskite Solar Cells efficiency under extreme heat conditions.",
            "skills": ["Material Science", "Physics", "Simulation"],
            "professor": "Prof. James Miller",
            "vacancies": "3 Field Researchers"
        })

    # 2. GENERATE APPLICATION (Now using EMAIL instead of Phone)
    application_text = f"""Subject: Application for Research Internship - {analysis_data['skills'][0]} Research

Dear {analysis_data['professor']},

I am {current_user.full_name}, a {current_user.qualification} student at {current_user.college}. I recently studied your paper linked at {data.get('url')} regarding "{analysis_data['summary'][:60]}...".

I was particularly impressed by the methodology described in the paper. Given my background in {', '.join(analysis_data['skills'][:2])}, I believe I can contribute effectively to your lab's ongoing projects.

I have attached my resume for your review and would welcome the opportunity to discuss how my skills align with the open positions in your team.

Sincerely,
{current_user.full_name}
{current_user.email}"""  # <--- CHANGED HERE

    return jsonify({
        "application": application_text,
        "analysis": analysis_data
    })

@app.route('/professor')
@login_required
def professor():
    if current_user.role != 'Professor': return redirect('/student')
    # Show internships posted by THIS professor
    my_internships = Internship.query.filter_by(user_id=current_user.id).all()
    return render_template('professor.html', internships=my_internships)

@app.route('/post_internship', methods=['POST'])
@login_required
def post_internship():
    if current_user.role != 'Professor': return "Unauthorized"
    
    new_internship = Internship(
        title=request.form.get('title'),
        domain=request.form.get('domain'),
        description=request.form.get('description'),
        type=request.form.get('type'),
        user_id=current_user.id
    )
    db.session.add(new_internship)
    db.session.commit()
    return redirect('/professor')

@app.route('/view_applicants/<int:id>')
@login_required
def view_applicants(id):
    internship = Internship.query.get(id)
    if internship.user_id != current_user.id: return "Unauthorized"
    return render_template('applicants.html', internship=internship) # Simple list view

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')
# Add this inside app.py



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)