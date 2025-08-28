from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True)
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    daily_summary = db.Column(db.Text, nullable=False)
    journal_content = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(20), default='quick')  # quick or detailed
    questions = db.Column(db.Text)  # JSON string of questions
    answers = db.Column(db.Text)    # JSON string of answers
    tokens_used = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    mood_before = db.Column(db.String(50))
    mood_after = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful! Please login.'})
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent journal entries
    recent_entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .order_by(JournalEntry.entry_date.desc())\
        .limit(5).all()
    
    # Get mood data for the last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    mood_data = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= start_date,
        MoodEntry.entry_date <= end_date
    ).all()
    
    return render_template('dashboard.html', 
                         recent_entries=recent_entries,
                         mood_data=mood_data)

@app.route('/journal/new')
@login_required
def new_journal():
    return render_template('new_journal.html')

@app.route('/journal/create', methods=['POST'])
@login_required
def create_journal():
    data = request.get_json()
    
    # Create journal entry (without AI for now)
    entry = JournalEntry(
        user_id=current_user.id,
        entry_date=datetime.now().date(),
        daily_summary=data.get('daily_summary', ''),
        journal_content=data.get('journal_content', ''),
        mode=data.get('mode', 'quick'),
        questions=json.dumps([]),
        answers=json.dumps([]),
        tokens_used=0
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Journal entry created successfully!',
        'ai_insights': [],
        'tokens_used': 0
    })

@app.route('/journal/<int:entry_id>')
@login_required
def view_journal(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    return render_template('view_journal.html', entry=entry)

@app.route('/api/generate-questions', methods=['POST'])
@login_required
def generate_questions():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    mode = data.get('mode', 'quick')
    
    if not daily_summary:
        return jsonify({'success': False, 'message': 'Daily summary is required'})
    
    # Fallback questions without AI
    if mode == 'quick':
        questions = [
            "What emotions did you experience today?",
            "What did you learn about yourself?",
            "How did you handle challenges?"
        ]
    else:
        questions = [
            "What emotions did you experience today?",
            "What did you learn about yourself?",
            "How did you handle challenges?",
            "What relationships were important today?",
            "What would you do differently?"
        ]
    
    return jsonify({
        'success': True,
        'questions': questions,
        'tokens_used': 0
    })

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/mood', methods=['POST'])
@login_required
def save_mood():
    data = request.get_json()
    entry_date = datetime.now().date()
    
    # Check if mood entry already exists for today
    existing_entry = MoodEntry.query.filter_by(
        user_id=current_user.id,
        entry_date=entry_date
    ).first()
    
    if existing_entry:
        if data.get('mood_before'):
            existing_entry.mood_before = data['mood_before']
        if data.get('mood_after'):
            existing_entry.mood_after = data['mood_after']
    else:
        new_entry = MoodEntry(
            user_id=current_user.id,
            entry_date=entry_date,
            mood_before=data.get('mood_before'),
            mood_after=data.get('mood_after')
        )
        db.session.add(new_entry)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/mood-analytics')
@login_required
def mood_analytics():
    # Get mood data for the last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= start_date,
        MoodEntry.entry_date <= end_date
    ).order_by(MoodEntry.entry_date.asc()).all()
    
    # Prepare data for charts
    dates = [entry.entry_date.strftime('%Y-%m-%d') for entry in mood_entries]
    moods_before = [entry.mood_before for entry in mood_entries if entry.mood_before]
    moods_after = [entry.mood_after for entry in mood_entries if entry.mood_after]
    
    return render_template('mood_analytics.html', 
                         mood_entries=mood_entries,
                         dates=dates,
                         moods_before=moods_before,
                         moods_after=moods_after)

@app.route('/api/mood/analytics')
@login_required
def get_mood_analytics():
    """API endpoint to get mood analytics data"""
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get mood entries with journal information
    mood_entries = db.session.query(
        MoodEntry, JournalEntry.id.label('journal_id')
    ).outerjoin(
        JournalEntry, 
        (MoodEntry.user_id == JournalEntry.user_id) & 
        (MoodEntry.entry_date == JournalEntry.entry_date)
    ).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= start_date,
        MoodEntry.entry_date <= end_date
    ).order_by(MoodEntry.entry_date.asc()).all()
    
    # Prepare data for frontend
    mood_data = []
    for mood_entry, journal_entry in mood_entries:
        mood_data.append({
            'entry_date': mood_entry.entry_date.strftime('%Y-%m-%d'),
            'mood_before': mood_entry.mood_before,
            'mood_after': mood_entry.mood_after,
            'journal_id': journal_entry.journal_id if journal_entry else None,
            'created_at': mood_entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'mood_data': mood_data,
        'total_entries': len(mood_data),
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
