from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

# AI Service class integrated directly into app.py
class AIService:
    def __init__(self):
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.available = True
            else:
                self.available = False
        except ImportError:
            print("OpenAI or dotenv not available, AI features will use fallbacks")
            self.available = False
        
    def generate_reflection_questions(self, daily_summary, mode='quick'):
        """Generate AI-powered reflection questions based on daily summary"""
        if not self.available:
            return self._get_fallback_questions(mode), 0
            
        try:
            if mode == 'quick':
                prompt = f"""You are a warm, supportive journaling companion. Based on this person's day: "{daily_summary}"

                Generate exactly 3 personalized reflection questions that feel like they're coming from a caring friend who knows them well. 
                
                Guidelines:
                - Make questions specific to their actual experiences and activities mentioned
                - Use warm, conversational language ("How did that feel?" vs "What emotions did you experience?")
                - Focus on emotional processing and self-discovery
                - Avoid overly clinical or therapy-like language
                - Make them feel seen and understood
                - Reference specific events or activities they mentioned
                - Ask about emotional transitions or mood changes they might have experienced
                
                Return only the questions, one per line, without numbering or extra text."""
            else:
                prompt = f"""You are a thoughtful journaling companion helping someone do deep self-reflection. Based on their day: "{daily_summary}"

                Generate exactly 5 personalized questions that encourage profound self-exploration. 
                
                Guidelines:
                - Make questions deeply personal and specific to their situation
                - Use warm, encouraging language that invites vulnerability
                - Focus on emotional depth, personal growth, and life insights
                - Help them connect their experiences to broader life patterns
                - Encourage self-compassion and understanding
                - Make questions that feel like they're coming from someone who truly cares
                
                Return only the questions, one per line, without numbering or extra text."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            questions = [q.strip() for q in questions if q.strip()]
            
            return questions, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_questions(mode), 0
    
    def enhance_journal_entry(self, daily_summary, journal_content, mode='quick'):
        """Enhance journal entry with AI insights"""
        if not self.available:
            return self._get_fallback_insights(mode), 0
            
        try:
            if mode == 'quick':
                prompt = f"""Daily Summary: {daily_summary}
                Journal Content: {journal_content}
                
                Provide 2-3 brief insights or observations about this journal entry. Focus on:
                - Emotional patterns
                - Growth opportunities
                - Positive aspects
                
                Keep insights concise and encouraging. Return only the insights, one per line."""
            else:
                prompt = f"""Daily Summary: {daily_summary}
                Journal Content: {journal_content}
                
                Provide 3-5 thoughtful insights about this journal entry. Focus on:
                - Emotional depth and patterns
                - Personal growth and learning
                - Relationship insights
                - Life wisdom and lessons
                - Future considerations
                
                Make insights meaningful and actionable. Return only the insights, one per line."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content.strip().split('\n')
            insights = [i.strip() for i in insights if i.strip()]
            
            return insights, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_insights(mode), 0
    
    def _get_fallback_questions(self, mode):
        """Fallback questions when AI is not available"""
        if mode == 'quick':
            return [
                "What was the highlight of your day?",
                "What challenged you today?",
                "What are you grateful for?",
                "How did you feel overall?"
            ]
        else:
            return [
                "What emotions did you experience today?",
                "What did you learn about yourself?",
                "How did you handle challenges?",
                "What would you do differently?",
                "What are you looking forward to tomorrow?"
            ]
    
    def _get_fallback_insights(self, mode):
        """Fallback insights when AI is not available"""
        if mode == 'quick':
            return [
                "Thank you for taking time to reflect on your day.",
                "Every reflection brings new insights and growth."
            ]
        else:
            return [
                "Your detailed reflection shows deep self-awareness.",
                "This kind of introspection leads to meaningful growth.",
                "You're building valuable self-knowledge through journaling."
            ]
    
    def is_available(self):
        """Check if AI service is available"""
        return self.available
    
    def generate_journal_summary(self, daily_summary, mode='quick'):
        """Generate a comprehensive summary of the journal entry"""
        if not self.available:
            return self._get_fallback_summary(daily_summary, mode), 0
            
        try:
            prompt = f"""You're helping someone create a meaningful summary of their day: "{daily_summary}"

            Write a thoughtful summary that captures the essence of their experience. 
            
            Guidelines:
            - Focus on what matters most to them emotionally and personally
            - Highlight key moments, feelings, and insights
            - Use warm, reflective language that honors their experience
            - Help them see patterns or growth in their day
            - Make it feel like a caring friend's perspective on their day
            - Avoid being overly clinical or generic
            
            Write as if you're helping them remember and appreciate their day. {f"Keep it to 2-3 sentences for quick mode" if mode == 'quick' else "4-5 sentences for detailed mode"}."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_summary(daily_summary, mode), 0
    
    def generate_assistant_response(self, daily_summary, journal_content, mode='quick'):
        """Generate an interactive assistant response to help with journaling"""
        if not self.available:
            return self._get_fallback_assistant_response(mode), 0
            
        try:
            prompt = f"""You're a warm, supportive friend who just read someone's journal entry about their day.

            Their day: {daily_summary}
            What they wrote: {journal_content}
            
            Respond as a caring friend would:
            - Show genuine understanding and empathy
            - Reflect back what you heard with warmth
            - Offer gentle insights or observations
            - Ask one thoughtful follow-up question if appropriate
            - Validate their experience and feelings
            - Be encouraging without being overly positive
            
            Sound like someone who truly cares about them, not an AI or therapist.
            Keep it conversational and heartfelt."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content.strip()
            return assistant_response, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_assistant_response(mode), 0
    
    def generate_mood_response(self, daily_summary, journal_content, mood, mode='quick'):
        """Generate a response based on the user's mood to help explore emotions"""
        if not self.available:
            return self._get_fallback_mood_response(mood, mode), 0
            
        try:
            prompt = f"""Daily Summary: {daily_summary}
            Journal Content: {journal_content}
            Current Mood: {mood}
            
            As a supportive journaling assistant, respond to their mood change:
            - Acknowledge their emotional state with empathy
            - Help them explore why they might be feeling this way
            - Connect their mood to the events they described
            - Offer gentle guidance for emotional processing
            
            Be warm, understanding, and helpful. Help them gain insight into their emotions."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            
            mood_response = response.choices[0].message.content.strip()
            return mood_response, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_mood_response(mood, mode), 0
    
    def _get_fallback_summary(self, daily_summary, mode):
        """Fallback summary when AI is not available"""
        if mode == 'quick':
            return f"Based on your summary about {daily_summary[:30]}..., you've had an eventful day. Your reflection shows thoughtful consideration of your experiences."
        else:
            return f"Your detailed summary about {daily_summary[:30]}... reveals a day filled with meaningful experiences. Your thoughtful reflection demonstrates deep self-awareness and emotional intelligence."
    
    def _get_fallback_assistant_response(self, mode):
        """Fallback assistant response when AI is not available"""
        if mode == 'quick':
            return "I'm reading your journal entry and finding it very insightful. Your reflection shows good self-awareness. Consider what patterns you notice in your experiences."
        else:
            return "Your detailed reflection is impressive! I can see you're really processing your experiences deeply. What connections do you see between today's events and your broader life journey?"
    
    def _get_fallback_mood_response(self, mood, mode):
        """Fallback mood response when AI is not available"""
        mood_responses = {
            'happy': "It's wonderful that you're feeling happy! This positive mood can really enhance your reflection. What contributed to this happiness today?",
            'calm': "Feeling calm is such a valuable state for reflection. Your peaceful mood suggests you're in a good space to process your experiences.",
            'neutral': "A neutral mood can actually be perfect for objective reflection. You're able to look at your day with balanced perspective.",
            'anxious': "I notice you're feeling anxious. This emotion can provide important insights into what matters to you. What's underlying this anxiety?",
            'sad': "I hear that you're feeling sad. This emotion is valid and can teach us important things about ourselves. What's bringing up these feelings?"
        }
        return mood_responses.get(mood, "Your mood is an important part of your journaling experience. How does this emotional state relate to what happened today?")
    
    def generate_conversational_questions(self, daily_summary, mode='quick'):
        """Generate conversational questions focused on emotions and feelings"""
        if not self.available:
            return self._get_fallback_conversational_questions(mode), 0
            
        try:
            if mode == 'quick':
                prompt = f"""You're having a heartfelt conversation with someone about their day: "{daily_summary}"

                Ask exactly 3 follow-up questions that show you're really listening and care about their experience. 
                
                Guidelines:
                - Be genuinely curious about their emotional experience
                - Use natural, conversational language ("That sounds..." "I'm curious about...")
                - Acknowledge both positive and difficult emotions
                - Make them feel heard and validated
                - Avoid generic questions - be specific to their situation
                
                Return only the questions, one per line, without numbering or extra text."""
            else:
                prompt = f"""You're having a deep, meaningful conversation with someone about their day: "{daily_summary}"

                Ask exactly 5 thoughtful follow-up questions that help them process their experience more deeply.
                
                Guidelines:
                - Show genuine empathy and understanding
                - Use warm, supportive language that invites sharing
                - Help them explore the emotional layers of their experience
                - Encourage self-reflection and personal growth
                - Validate their feelings while gently encouraging deeper exploration
                - Make questions that feel like they're coming from someone who truly understands
                
                Return only the questions, one per line, without numbering or extra text."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            questions = [q.strip() for q in questions if q.strip()]
            
            return questions, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_conversational_questions(mode), 0
    
    def generate_conversational_summary(self, daily_summary, user_answers, mode='quick'):
        """Generate a conversational summary that preserves raw emotions"""
        if not self.available:
            return self._get_fallback_conversational_summary(daily_summary, user_answers, mode), 0
            
        try:
            prompt = f"""You're a caring friend who just listened to someone share about their day. Here's what they told you:

            Daily Summary: {daily_summary}
            
            Their responses to your questions:
            {chr(10).join([f"Q{i+1}: {answer}" for i, answer in enumerate(user_answers)])}
            
            Write a warm, empathetic summary that:
            - Reflects back what you heard with genuine understanding
            - Honors their emotional experience without judgment
            - Uses their own words and emotional tone when possible
            - Shows you truly listened and care about their experience
            - Validates their feelings while highlighting any growth or insights
            - Sounds like a supportive friend, not a therapist or AI
            
            Keep it conversational and heartfelt. {f"3-4 sentences for quick mode" if mode == 'quick' else "5-6 sentences for detailed mode"}."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary, response.usage.total_tokens
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_conversational_summary(daily_summary, user_answers, mode), 0
    
    def _get_fallback_conversational_questions(self, mode):
        """Fallback conversational questions when AI is not available"""
        if mode == 'quick':
            return [
                "How did you feel about what happened today?",
                "What was the most challenging part of your day?",
                "What would you do differently if you could?"
            ]
        else:
            return [
                "How did you feel about what happened today?",
                "What was the most challenging part of your day?",
                "What emotions came up during these events?",
                "How did you handle any difficult situations?",
                "What did you learn about yourself today?",
                "What would you do differently if you could?"
            ]
    
    def _get_fallback_conversational_summary(self, daily_summary, user_answers, mode):
        """Fallback conversational summary when AI is not available"""
        summary = f"Today you experienced: {daily_summary[:100]}... "
        
        if user_answers:
            summary += "You reflected on your feelings and responses to these events. "
            if mode == 'detailed':
                summary += "Your detailed answers show deep consideration of your emotional experience and personal growth."
            else:
                summary += "Your answers show thoughtful consideration of your experiences."
        
        return summary

# Initialize AI service
ai = AIService()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
# Database configuration - supports both SQLite (local) and PostgreSQL (production)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Production: PostgreSQL (Railway, Heroku, etc.)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development: SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Custom Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to Python object"""
    try:
        if isinstance(value, str):
            # Clean up any potential encoding issues
            cleaned_value = value.strip()
            if cleaned_value:
                # Handle potential encoding issues with quotes
                parsed = json.loads(cleaned_value)
                print(f"Successfully parsed JSON: {parsed}")
                return parsed
        return []
    except (ValueError, TypeError) as e:
        print(f"JSON parsing error: {e}, value: {repr(value)}")
        return []

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
    mood = db.Column(db.String(50), nullable=False)  # Single mood field
    notes = db.Column(db.Text)  # Optional notes about the mood
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
    ).order_by(MoodEntry.entry_date.desc()).all()
    
    return render_template('dashboard.html', 
                         recent_entries=recent_entries,
                         mood_data=mood_data)

@app.route('/journal/new')
@login_required
def new_journal():
    return render_template('new_journal.html')

# UPDATED: now uses AI to generate questions and insights, and stores them
@app.route('/journal/create', methods=['POST'])
@login_required
def create_journal():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    ai_questions = data.get('ai_questions', [])
    user_answers = data.get('user_answers', [])
    ai_summary = data.get('ai_summary', '')
    mode = data.get('mode', 'quick')

    # Store the AI questions and user answers
    questions_json = json.dumps(ai_questions)
    answers_json = json.dumps(user_answers)
    
    # Use AI summary if provided, otherwise generate one
    if not ai_summary:
        try:
            ai_summary, tokens = ai.generate_journal_summary(daily_summary, mode=mode)
        except Exception as e:
            print(f"AI error generating summary: {e}")
            ai_summary = f"Today you experienced: {daily_summary[:100]}... You reflected on your feelings and responses to these events."
            tokens = 0
    else:
        tokens = 0  # Summary was already generated

    entry = JournalEntry(
        user_id=current_user.id,
        entry_date=datetime.now().date(),
        daily_summary=daily_summary,
        journal_content=ai_summary,  # Store AI summary as journal content
        mode=mode,
        questions=questions_json,
        answers=answers_json,  # Store user answers
        tokens_used=tokens
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Journal entry created successfully!',
        'entry_id': entry.id
    })

@app.route('/journal/<int:entry_id>')
@login_required
def view_journal(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Debug: Print what's stored in the database
    print(f"Viewing journal entry {entry_id}:")
    print(f"Questions (raw): {entry.questions}")
    print(f"Answers (raw): {entry.answers}")
    print(f"Tokens used: {entry.tokens_used}")
    
    return render_template('view_journal.html', entry=entry)

# UPDATED: now calls AIService with graceful fallback
@app.route('/api/generate-questions', methods=['POST'])
@login_required
def generate_questions():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    mode = data.get('mode', 'quick')
    
    if not daily_summary:
        return jsonify({'success': False, 'message': 'Daily summary is required'})
    
    try:
        questions, tokens = ai.generate_reflection_questions(daily_summary, mode=mode)
    except Exception as e:
        print(f"AI error in /api/generate-questions: {e}")
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
        tokens = 0
    
    return jsonify({
        'success': True,
        'questions': questions,
        'tokens_used': tokens
    })

# NEW: Live AI insights endpoint for real-time journal analysis
@app.route('/api/generate-live-insights', methods=['POST'])
@login_required
def generate_live_insights():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    journal_content = data.get('journal_content', '')
    mode = data.get('mode', 'quick')
    
    if not daily_summary or not journal_content:
        return jsonify({'success': False, 'message': 'Both daily summary and journal content are required'})
    
    try:
        insights, tokens = ai.enhance_journal_entry(daily_summary, journal_content, mode=mode)
    except Exception as e:
        print(f"AI error in /api/generate-live-insights: {e}")
        # Provide encouraging fallback insights
        if mode == 'quick':
            insights = [
                "Your reflection is developing nicely!",
                "Keep writing to explore your thoughts further.",
                "This is a great start to your journal entry."
            ]
        else:
            insights = [
                "Your detailed reflection shows deep thinking.",
                "Consider how this experience relates to your broader life.",
                "You're building valuable self-awareness through this process."
            ]
        tokens = 0
    
    return jsonify({
        'success': True,
        'insights': insights,
        'tokens_used': tokens
    })

# NEW: AI Journaling Assistant endpoint for interactive journaling
@app.route('/api/generate-ai-response', methods=['POST'])
@login_required
def generate_ai_response():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    journal_content = data.get('journal_content', '')
    mood = data.get('mood', '')
    response_type = data.get('type', 'summary')
    mode = data.get('mode', 'quick')
    
    print(f"AI Response Request - Type: {response_type}, Mode: {mode}, Summary: {daily_summary[:50]}...")
    
    if not daily_summary:
        return jsonify({'success': False, 'message': 'Daily summary is required'})
    
    try:
        if response_type == 'summary':
            # Generate initial summary based on daily summary
            summary, tokens = ai.generate_journal_summary(daily_summary, mode=mode)
            print(f"Generated summary: {summary[:100]}...")
            return jsonify({
                'success': True,
                'summary': summary,
                'tokens_used': tokens
            })
        
        elif response_type == 'content':
            # Generate assistant response based on journal content
            assistant_response, tokens = ai.generate_assistant_response(daily_summary, journal_content, mode=mode)
            print(f"Generated assistant response: {assistant_response[:100]}...")
            return jsonify({
                'success': True,
                'assistant_response': assistant_response,
                'tokens_used': tokens
            })
        
        elif response_type == 'mood':
            # Generate response based on mood change
            mood_response, tokens = ai.generate_mood_response(daily_summary, journal_content, mood, mode=mode)
            print(f"Generated mood response: {mood_response[:100]}...")
            return jsonify({
                'success': True,
                'assistant_response': mood_response,
                'tokens_used': tokens
            })
        
        else:
            return jsonify({'success': False, 'message': 'Invalid response type'})
            
    except Exception as e:
        print(f"AI error in /api/generate-ai-response: {e}")
        
        # Provide helpful fallback responses
        if response_type == 'summary':
            fallback = f"Based on your summary: '{daily_summary[:50]}...', I can see you've had an eventful day. Keep writing to explore your thoughts further."
        elif response_type == 'content':
            fallback = "I'm reading your journal entry and finding it very insightful. Consider exploring how this experience relates to your broader life goals and values."
        elif response_type == 'mood':
            mood_emojis = {'happy': '😊', 'calm': '😌', 'neutral': '😐', 'anxious': '😰', 'sad': '😢'}
            emoji = mood_emojis.get(mood, '😊')
            fallback = f"I notice you're feeling {mood} {emoji}. This mood can provide valuable context for understanding your day. How does this feeling relate to what happened today?"
        
        print(f"Using fallback response: {fallback[:100]}...")
        
        if response_type == 'summary':
            return jsonify({
                'success': True,
                'summary': fallback,
                'tokens_used': 0
            })
        else:
            return jsonify({
                'success': True,
                'assistant_response': fallback,
                'tokens_used': 0
            })

# NEW: Generate AI questions based on daily summary
@app.route('/api/generate-ai-questions', methods=['POST'])
@login_required
def generate_ai_questions():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    mode = data.get('mode', 'quick')
    
    print(f"=== AI Questions Request ===")
    print(f"Daily Summary: {daily_summary[:100]}...")
    print(f"Mode: {mode}")
    
    if not daily_summary:
        return jsonify({'success': False, 'message': 'Daily summary is required'})
    
    try:
        print(f"Calling AI service...")
        questions, tokens = ai.generate_conversational_questions(daily_summary, mode=mode)
        print(f"AI Success! Questions: {questions}")
        print(f"Tokens used: {tokens}")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'tokens_used': tokens
        })
    except Exception as e:
        print(f"AI Error Details: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Provide fallback questions
        if mode == 'quick':
            questions = [
                "How did you feel about what happened today?",
                "What was the most challenging part of your day?",
                "What would you do differently if you could?"
            ]
        else:
            questions = [
                "How did you feel about what happened today?",
                "What was the most challenging part of your day?",
                "What emotions came up during these events?",
                "How did you handle any difficult situations?",
                "What did you learn about yourself today?",
                "What would you do differently if you could?"
            ]
        
        print(f"Using fallback questions: {questions}")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'tokens_used': 0
        })

# NEW: Generate AI summary based on daily summary and user answers
@app.route('/api/generate-journal-summary', methods=['POST'])
@login_required
def generate_journal_summary():
    data = request.get_json()
    daily_summary = data.get('daily_summary', '')
    user_answers = data.get('user_answers', [])
    mode = data.get('mode', 'quick')
    
    if not daily_summary:
        return jsonify({'success': False, 'message': 'Daily summary is required'})
    
    try:
        summary, tokens = ai.generate_conversational_summary(daily_summary, user_answers, mode=mode)
        return jsonify({
            'success': True,
            'summary': summary,
            'tokens_used': tokens
        })
    except Exception as e:
        print(f"AI error in /api/generate-journal-summary: {e}")
        # Provide fallback summary
        fallback = f"Today you experienced: {daily_summary[:100]}... You reflected on your feelings and responses to these events. Your answers show thoughtful consideration of your experiences."
        
        return jsonify({
            'success': True,
            'summary': fallback,
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
    mood = data.get('mood')
    notes = data.get('notes', '')
    entry_date = datetime.now().date()
    
    if not mood:
        return jsonify({'success': False, 'message': 'Mood is required'})
    
    # Check if mood entry already exists for today
    existing_entry = MoodEntry.query.filter_by(
        user_id=current_user.id,
        entry_date=entry_date
    ).first()
    
    if existing_entry:
        # Update existing entry
        existing_entry.mood = mood
        existing_entry.notes = notes
    else:
        # Create new entry
        new_entry = MoodEntry(
            user_id=current_user.id,
            entry_date=entry_date,
            mood=mood,
            notes=notes
        )
        db.session.add(new_entry)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Mood saved successfully!'})

@app.route('/mood-checkin')
@login_required
def mood_checkin():
    """Simple mood check-in page"""
    return render_template('mood_checkin.html')

@app.route('/mood-analytics')
@login_required
def mood_analytics():
    """Mood analytics page"""
    return render_template('mood_analytics.html')

@app.route('/api/mood/analytics')
@login_required
def get_mood_analytics():
    """API endpoint to get mood analytics data"""
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get mood entries for the specified date range
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= start_date,
        MoodEntry.entry_date <= end_date
    ).order_by(MoodEntry.entry_date.asc()).all()
    
    # Prepare data for frontend
    mood_data = []
    for entry in mood_entries:
        mood_data.append({
            'entry_date': entry.entry_date.strftime('%Y-%m-%d'),
            'mood': entry.mood,
            'notes': entry.notes,
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
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
