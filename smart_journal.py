import streamlit as st
import openai
import json
import sqlite3
import os
from datetime import datetime, timedelta
import calendar
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Smart Journal Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
def init_openai():
    """Initialize OpenAI client with API key from environment or user input"""
    # Try to get API key from environment variables first
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # If not in environment, try Streamlit secrets
        api_key = st.secrets.get("OPENAI_API_KEY")
    
    if not api_key:
        # If still not found, ask user to input it
        st.warning("🔐 OpenAI API key not found in environment variables or secrets.")
        st.info("For security, please set your API key as an environment variable or add it to .streamlit/secrets.toml")
        
        # Create a secure input field
        api_key = st.text_input(
            "Enter your OpenAI API key:",
            type="password",
            help="Your API key will not be stored permanently. For production, use environment variables.",
            placeholder="sk-..."
        )
        
        if not api_key:
            st.error("⚠️ OpenAI API key is required to use this app.")
            st.stop()
        elif not api_key.startswith("sk-"):
            st.error("⚠️ Please enter a valid OpenAI API key (should start with 'sk-').")
            st.stop()
    
    return openai.OpenAI(api_key=api_key)

# Token tracking functions
def load_token_usage():
    """Load token usage from file"""
    try:
        with open('token_usage.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_tokens": 0, "month": datetime.now().strftime("%Y-%m")}

def save_token_usage(usage):
    """Save token usage to file"""
    with open('token_usage.json', 'w') as f:
        json.dump(usage, f)

def update_token_usage(tokens_used):
    """Update token usage tracking"""
    usage = load_token_usage()
    current_month = datetime.now().strftime("%Y-%m")
    
    # Reset if new month
    if usage["month"] != current_month:
        usage = {"total_tokens": 0, "month": current_month}
    
    usage["total_tokens"] += tokens_used
    save_token_usage(usage)
    return usage

def check_token_limit():
    """Check if user is within token limit"""
    usage = load_token_usage()
    current_month = datetime.now().strftime("%Y-%m")
    
    # Reset if new month
    if usage["month"] != current_month:
        return True, 0
    
    # Get limit from environment variables, then secrets, then default
    limit = int(os.getenv("TOKEN_LIMIT", st.secrets.get("TOKEN_LIMIT", 40000)))
    return usage["total_tokens"] < limit, usage["total_tokens"]

# Mood tracking functions
def load_mood_data():
    """Load mood data from file"""
    try:
        with open('mood_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_mood_data(mood_data):
    """Save mood data to file"""
    with open('mood_data.json', 'w') as f:
        json.dump(mood_data, f)

def get_mood_color(mood):
    """Get color for mood"""
    colors = {
        'happy': '#4CAF50',      # Green
        'calm': '#2196F3',       # Blue
        'sad': '#9E9E9E',        # Gray
        'stressed': '#FF9800',    # Orange
        'angry': '#F44336',       # Red
        'tired': '#9C27B0',      # Purple
        'neutral': '#FFEB3B'      # Yellow
    }
    return colors.get(mood, '#E0E0E0')

def get_mood_emoji(mood):
    """Get emoji for mood"""
    emojis = {
        'happy': '😊',
        'calm': '😌',
        'sad': '😔',
        'stressed': '😤',
        'angry': '😡',
        'tired': '😴',
        'neutral': '😐'
    }
    return emojis.get(mood, '❓')

def create_mood_calendar(mood_data, year, month):
    """Create a calendar view with mood colors"""
    cal = calendar.monthcalendar(year, month)
    
    # Create calendar HTML
    calendar_html = f"""
    <div style="text-align: center; margin: 20px 0;">
        <table style="width: 100%; border-collapse: collapse; margin: 0 auto;">
            <tr>
                <th style="padding: 10px; border: 1px solid #ddd;">Sun</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Mon</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Tue</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Wed</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Thu</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Fri</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Sat</th>
            </tr>
    """
    
    for week in cal:
        calendar_html += "<tr>"
        for day in week:
            if day == 0:
                calendar_html += '<td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;"></td>'
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                mood = mood_data.get(date_str, None)
                
                if mood:
                    color = get_mood_color(mood)
                    emoji = get_mood_emoji(mood)
                    calendar_html += f'<td style="padding: 10px; border: 1px solid #ddd; background-color: {color}; text-align: center;">{day}<br><span style="font-size: 12px;">{emoji}</span></td>'
                else:
                    calendar_html += f'<td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{day}</td>'
        calendar_html += "</tr>"
    
    calendar_html += "</table></div>"
    return calendar_html

def mood_selection_ui():
    """Create mood selection UI"""
    st.markdown("### How are you feeling?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    moods = {
        'happy': ('😊 Happy', '#4CAF50'),
        'calm': ('😌 Calm', '#2196F3'),
        'sad': ('😔 Sad', '#9E9E9E'),
        'stressed': ('😤 Stressed', '#FF9800'),
        'angry': ('😡 Angry', '#F44336'),
        'tired': ('😴 Tired', '#9C27B0'),
        'neutral': ('😐 Neutral', '#FFEB3B')
    }
    
    selected_mood = None
    
    with col1:
        if st.button("😊 Happy", key="mood_happy", use_container_width=True):
            selected_mood = "happy"
        if st.button("😌 Calm", key="mood_calm", use_container_width=True):
            selected_mood = "calm"
    
    with col2:
        if st.button("😔 Sad", key="mood_sad", use_container_width=True):
            selected_mood = "sad"
        if st.button("😤 Stressed", key="mood_stressed", use_container_width=True):
            selected_mood = "stressed"
    
    with col3:
        if st.button("😡 Angry", key="mood_angry", use_container_width=True):
            selected_mood = "angry"
        if st.button("😴 Tired", key="mood_tired", use_container_width=True):
            selected_mood = "tired"
    
    with col4:
        if st.button("😐 Neutral", key="mood_neutral", use_container_width=True):
            selected_mood = "neutral"
    
    return selected_mood

def mood_analytics_ui(mood_data):
    """Display mood analytics"""
    if not mood_data:
        st.info("📊 No mood data yet. Start journaling to see your mood trends!")
        return
    
    st.subheader("Mood Analytics")
    
    # Convert to DataFrame for analysis
    dates = []
    moods = []
    for date, mood in mood_data.items():
        dates.append(datetime.strptime(date, '%Y-%m-%d'))
        moods.append(mood)
    
    df = pd.DataFrame({'date': dates, 'mood': moods})
    
    # Simple analytics without complex charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Mood Distribution**")
        mood_counts = df['mood'].value_counts()
        
        # Display mood counts as simple text
        for mood, count in mood_counts.items():
            emoji = get_mood_emoji(mood)
            percentage = (count / len(df)) * 100
            st.write(f"{emoji} **{mood.title()}**: {count} times ({percentage:.1f}%)")
    
    with col2:
        st.write("**Journaling Statistics**")
        # Get journal entries data for analysis
        entries_data = get_journal_entries(limit=100)  # Get more entries for better stats
        if entries_data:
            # Count entries per day
            entry_counts = {}
            for entry in entries_data:
                # Parse the date and format it nicely
                try:
                    date_obj = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S.%f')
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    # Fallback for different date formats
                    date_str = entry['date'].split(' ')[0]  # Take just the date part
                
                if date_str in entry_counts:
                    entry_counts[date_str] += 1
                else:
                    entry_counts[date_str] = 1
            
            # Calculate statistics
            if entry_counts:
                total_entries = sum(entry_counts.values())
                total_days = len(entry_counts)
                avg_entries_per_day = total_entries / total_days if total_days > 0 else 0
                max_entries_in_day = max(entry_counts.values()) if entry_counts else 0
                days_with_entries = len([count for count in entry_counts.values() if count > 0])
                
                st.write(f"📊 **Total Entries:** {total_entries}")
                st.write(f"📅 **Days with Entries:** {days_with_entries}")
                st.write(f"📈 **Average per Day:** {avg_entries_per_day:.1f}")
                st.write(f"🔥 **Most in One Day:** {max_entries_in_day}")
                
                # Show recent activity
                st.write("**Recent Activity:**")
                recent_days = sorted(entry_counts.items())[-5:]  # Show last 5 days
                for date, count in recent_days:
                    st.write(f"📝 **{date}**: {count} entries")
            else:
                st.info("No journal entries found in the selected period.")
        else:
            st.info("No journal entries yet. Start journaling to see your writing patterns!")
    
    # Mood insights
    st.write("**Insights**")
    if len(df) > 1:
        most_common_mood = df['mood'].mode().iloc[0] if not df['mood'].mode().empty else "No pattern yet"
        total_entries = len(df)
        st.write(f"• Most common mood: **{most_common_mood.title()}**")
        st.write(f"• Total mood entries: **{total_entries}**")
        st.write(f"• Date range: **{df['date'].min().strftime('%B %d, %Y')}** to **{df['date'].max().strftime('%B %d, %Y')}**")
    else:
        st.write("• Keep journaling to see your mood patterns!")

def get_mood_analytics(mood_data):
    """Analyze mood data for trends and patterns"""
    if not mood_data:
        return {}
    
    # Convert date strings to datetime objects for easier processing
    dates = [datetime.strptime(d, '%Y-%m-%d') for d in mood_data.keys()]
    moods = [m for m in mood_data.values()]
    
    # Create a DataFrame
    df = pd.DataFrame({
        'date': dates,
        'mood': moods
    })
    
    # Group by date and calculate average mood
    avg_mood_by_date = df.groupby('date')['mood'].mean().reset_index()
    avg_mood_by_date.rename(columns={'mood': 'average_mood'}, inplace=True)
    
    # Group by mood and count occurrences
    mood_counts = df['mood'].value_counts().reset_index()
    mood_counts.rename(columns={'index': 'mood', 'mood': 'count'}, inplace=True)
    
    # Sort by date for plotting
    avg_mood_by_date.sort_values(by='date', inplace=True)
    
    return {
        'avg_mood_by_date': avg_mood_by_date.to_dict('records'),
        'mood_counts': mood_counts.to_dict('records')
    }

# Database functions
def init_database():
    """Initialize SQLite database and create tables"""
    conn = sqlite3.connect('journal_entries.db')
    cursor = conn.cursor()
    
    # Create journal entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mode TEXT NOT NULL,
            summary TEXT,
            questions TEXT,
            answers TEXT,
            journal_entry TEXT,
            tokens_used INTEGER,
            mood_before TEXT,
            mood_after TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER,
            theme TEXT,
            emotion TEXT,
            coping_strategy TEXT,
            FOREIGN KEY (entry_id) REFERENCES journal_entries(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_journal_entry(mode, summary, questions, answers, journal_entry, tokens_used):
    """Save a journal entry to the database"""
    try:
        conn = sqlite3.connect('journal_entries.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO journal_entries 
            (date, mode, summary, questions, answers, journal_entry, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            mode,
            summary,
            questions,
            answers,
            journal_entry,
            tokens_used
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving journal entry: {str(e)}")
        return False

def get_journal_entries(limit=50, search_term=None, mode_filter=None):
    """Retrieve journal entries from database"""
    try:
        conn = sqlite3.connect('journal_entries.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM journal_entries WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (summary LIKE ? OR journal_entry LIKE ?)"
            params.extend([f'%{search_term}%', f'%{search_term}%'])
        
        if mode_filter:
            query += " AND mode = ?"
            params.append(mode_filter)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        entries = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        
        # Convert to list of dictionaries
        result = []
        for entry in entries:
            entry_dict = dict(zip(columns, entry))
            result.append(entry_dict)
        
        return result
    except Exception as e:
        st.error(f"Error retrieving journal entries: {str(e)}")
        return []

def get_quote_of_the_day():
    """Get a quote of the day based on current date"""
    quotes = [
        {
            "text": "The only way to do great work is to love what you do.",
            "author": "Steve Jobs"
        },
        {
            "text": "The journey of a thousand miles begins with one step.",
            "author": "Lao Tzu"
        },
        {
            "text": "What you get by achieving your goals is not as important as what you become by achieving your goals.",
            "author": "Zig Ziglar"
        },
        {
            "text": "The mind is everything. What you think you become.",
            "author": "Buddha"
        },
        {
            "text": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "author": "Winston Churchill"
        },
        {
            "text": "The best way to predict the future is to create it.",
            "author": "Peter Drucker"
        },
        {
            "text": "Life is what happens when you're busy making other plans.",
            "author": "John Lennon"
        },
        {
            "text": "The only limit to our realization of tomorrow is our doubts of today.",
            "author": "Franklin D. Roosevelt"
        },
        {
            "text": "Believe you can and you're halfway there.",
            "author": "Theodore Roosevelt"
        },
        {
            "text": "It does not matter how slowly you go as long as you do not stop.",
            "author": "Confucius"
        }
    ]
    
    # Use current date to select a quote (changes daily)
    current_date = datetime.now()
    day_of_year = current_date.timetuple().tm_yday
    quote_index = day_of_year % len(quotes)
    
    return quotes[quote_index]

def get_analytics():
    """Get basic analytics from journal entries"""
    try:
        conn = sqlite3.connect('journal_entries.db')
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total_entries = cursor.fetchone()[0]
        
        # Entries by mode
        cursor.execute("SELECT mode, COUNT(*) FROM journal_entries GROUP BY mode")
        mode_stats = cursor.fetchall()
        
        # Recent entries (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM journal_entries 
            WHERE date >= date('now', '-7 days')
        """)
        recent_entries = cursor.fetchone()[0]
        
        # Total tokens used
        cursor.execute("SELECT SUM(tokens_used) FROM journal_entries")
        total_tokens = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'mode_stats': dict(mode_stats),
            'recent_entries': recent_entries,
            'total_tokens': total_tokens
        }
    except Exception as e:
        st.error(f"Error getting analytics: {str(e)}")
        return {}

# Initialize database on startup
init_database()

# Custom CSS for clean, simple styling
st.markdown("""
<style>
    /* Clean, simple styling */
    .main-header {
        font-size: 6rem;
        font-weight: 900;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.04em;
    }
    
    .main-subtitle {
        font-size: 2.2rem !important;
        color: #6c757d !important;
        text-align: center;
        margin-bottom: 4rem;
        font-weight: 500 !important;
        line-height: 1.7;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Clean card styling */
    .journal-entry {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .question-box {
        background: #e3f2fd;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #bbdefb;
    }
    
    .mode-selector {
        background: transparent;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: none;
    }
    
    /* Uniform button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        background: #667eea;
        border: none;
        color: white;
        padding: 0.5rem 1.5rem;
        font-size: 0.9rem;
        white-space: nowrap;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stButton > button:hover {
        background: #5a6fd8;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Clean input styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        transition: all 0.2s ease;
        background: white;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress indicators */
    .progress-step {
        background: #e9ecef;
        color: #495057;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin: 0.25rem 0;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .progress-step.active {
        background: #667eea;
        color: white;
        font-weight: 600;
    }
    
    /* Quote of the Day styling */
    .quote-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .quote-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .quote-text {
        color: white;
        font-size: 1.1rem;
        font-style: italic;
        line-height: 1.6;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .quote-author {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
        text-align: right;
        font-weight: 500;
    }
    
    /* Enhanced styling improvements */
    .main-header {
        font-size: 6rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.04em;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Enhanced card styling */
    .journal-entry {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    .question-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 2px solid #2196f3;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        color: white !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        color: white !important;
    }
    
    .stButton > button:focus {
        color: white !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .main-subtitle {
            font-size: 1rem;
        }
        .quote-container {
            margin: 1rem 0;
            padding: 1.5rem;
        }
    }
    
    /* Hide anchor links next to headers */
    .stMarkdown h1::before,
    .stMarkdown h2::before,
    .stMarkdown h3::before,
    .stMarkdown h4::before,
    .stMarkdown h5::before,
    .stMarkdown h6::before {
        display: none !important;
    }
    
    /* Hide the anchor link icons */
    .stMarkdown h1 a,
    .stMarkdown h2 a,
    .stMarkdown h3 a,
    .stMarkdown h4 a,
    .stMarkdown h5 a,
    .stMarkdown h6 a {
        display: none !important;
    }
    
    /* Animation keyframes */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Apply animations to elements */
    .main-header {
        animation: slideInFromTop 1s ease-out;
    }
    
    .main-subtitle {
        animation: fadeInUp 1.2s ease-out 0.3s both;
    }
    
    .mode-selector {
        animation: fadeInScale 1s ease-out 0.6s both;
    }
    
    .quote-container {
        animation: slideInFromLeft 1s ease-out 0.8s both;
    }
    
    .section-header {
        animation: fadeInUp 0.8s ease-out;
    }
    
    .journal-entry {
        animation: fadeInScale 0.8s ease-out;
    }
    
    .question-box {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .stButton > button {
        animation: fadeInScale 0.5s ease-out;
    }
    
    /* Stagger animations for mood buttons */
    .stButton > button:nth-child(1) { animation-delay: 0.1s; }
    .stButton > button:nth-child(2) { animation-delay: 0.2s; }
    .stButton > button:nth-child(3) { animation-delay: 0.3s; }
    .stButton > button:nth-child(4) { animation-delay: 0.4s; }
    .stButton > button:nth-child(5) { animation-delay: 0.5s; }
    .stButton > button:nth-child(6) { animation-delay: 0.6s; }
    .stButton > button:nth-child(7) { animation-delay: 0.7s; }
</style>
""", unsafe_allow_html=True)

def generate_quick_journal_entry(client, summary):
    """Generate a complete journal entry directly from the summary using GPT-3.5-turbo"""
    try:
        # Check token limit before making request
        within_limit, current_usage = check_token_limit()
        if not within_limit:
            st.error(f"⚠️ Token limit reached! You've used {current_usage:,} tokens this month. Please wait until next month or increase your limit.")
            return None, 0
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a journaling assistant. Create natural, authentic journal entries that:
1. Sound like the user actually wrote them - not overly polished or formal
2. Only include details that were actually mentioned - don't assume or add things
3. Capture genuine emotions and thoughts - including negative ones
4. Are conversational and personal in tone
5. Include the date naturally
6. Keep it concise (200-300 words max)
7. Focus on the user's actual experience, not generic journaling
8. Don't force positivity - reflect the user's true feelings, even if negative
9. Don't assume positive outcomes - only state what the user actually said happened
10. Add reflective insights - help the user process their experience and gain self-awareness
11. Include personal growth moments - what they learned about themselves or the situation
12. Show emotional processing - how they're working through their feelings"""
                },
                {
                    "role": "user",
                    "content": f"Create a natural, authentic journal entry based on this summary: '{summary}'. Write it like the person actually wrote it themselves - conversational, personal, and ONLY including what they actually shared. Don't force positivity or assume positive outcomes. Reflect their true feelings, even if negative. Add reflective insights and help them process their experience. Bridge gaps naturally without adding assumptions. Include today's date ({datetime.now().strftime('%B %d, %Y')}) naturally in the entry."
                }
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        # Update token usage
        tokens_used = response.usage.total_tokens
        update_token_usage(tokens_used)
        
        return response.choices[0].message.content.strip(), tokens_used
    except Exception as e:
        st.error(f"Error generating journal entry: {str(e)}")
        return None, 0

def generate_quick_questions(client, summary):
    """Generate 3-4 simple follow-up questions for quick mode"""
    try:
        # Check token limit before making request
        within_limit, current_usage = check_token_limit()
        if not within_limit:
            st.error(f"⚠️ Token limit reached! You've used {current_usage:,} tokens this month. Please wait until next month or increase your limit.")
            return None
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a journaling assistant. Ask 3-4 simple, natural follow-up questions to help the user reflect on their day. Keep questions short and easy to answer quickly. Focus on feelings, insights, coping strategies, or gratitude."
                },
                {
                    "role": "user",
                    "content": f"Based on this summary: '{summary}', ask 3-4 simple follow-up questions to help the user reflect. Make them natural and easy to answer quickly. Format as a simple list."
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        # Update token usage
        tokens_used = response.usage.total_tokens
        update_token_usage(tokens_used)
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return None

def generate_quick_journal_with_answers(client, summary, answers):
    """Generate journal entry from summary and quick answers"""
    try:
        # Check token limit before making request
        within_limit, current_usage = check_token_limit()
        if not within_limit:
            st.error(f"⚠️ Token limit reached! You've used {current_usage:,} tokens this month. Please wait until next month or increase your limit.")
            return None, 0
        
        # Combine summary and answers
        context = f"Daily Summary: {summary}\n\nQuick Answers:\n{answers}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a journaling assistant. Create natural, authentic journal entries that:
1. Sound like the user actually wrote them - not overly polished or formal
2. Only include details that were actually mentioned - don't assume or add things
3. Capture genuine emotions and thoughts - including negative ones
4. Are conversational and personal in tone
5. Include the date naturally
6. Keep it concise (200-300 words max)
7. Focus on the user's actual experience, not generic journaling
8. Don't force positivity - reflect the user's true feelings, even if negative
9. Don't assume positive outcomes - only state what the user actually said happened
10. Add reflective insights - help the user process their experience and gain self-awareness
11. Include personal growth moments - what they learned about themselves or the situation
12. Show emotional processing - how they're working through their feelings"""
                },
                {
                    "role": "user",
                    "content": f"Create a natural, authentic journal entry using this summary and the user's answers: {context}. Write it like the person actually wrote it themselves - conversational, personal, and ONLY including what they actually shared. Don't force positivity or assume positive outcomes. Reflect their true feelings, even if negative. Add reflective insights and help them process their experience. Bridge gaps naturally without adding assumptions. Include today's date ({datetime.now().strftime('%B %d, %Y')}) naturally in the entry."
                }
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        # Update token usage
        tokens_used = response.usage.total_tokens
        update_token_usage(tokens_used)
        
        return response.choices[0].message.content.strip(), tokens_used
    except Exception as e:
        st.error(f"Error generating journal entry: {str(e)}")
        return None, 0

def generate_follow_up_questions(client, summary):
    """Generate follow-up questions using GPT-3.5-turbo"""
    try:
        # Check token limit before making request
        within_limit, current_usage = check_token_limit()
        if not within_limit:
            st.error(f"⚠️ Token limit reached! You've used {current_usage:,} tokens this month. Please wait until next month or increase your limit.")
            return None
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a thoughtful journaling assistant. Your goal is to help users create meaningful, reflective journal entries by asking insightful follow-up questions."
                },
                {
                    "role": "user",
                    "content": f"The user shared this daily summary: '{summary}'. Ask 6-8 meaningful follow-up questions that will help them reflect deeper on their day. Make the questions specific and thought-provoking. Focus on emotions, insights, coping strategies, personal growth, and deeper reflection. Format your response as a simple list with each question on a new line."
                }
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        # Update token usage
        tokens_used = response.usage.total_tokens
        update_token_usage(tokens_used)
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return None

def generate_journal_entry(client, summary, answers):
    """Generate a reflective journal entry using GPT-3.5-turbo"""
    try:
        # Check token limit before making request
        within_limit, current_usage = check_token_limit()
        if not within_limit:
            st.error(f"⚠️ Token limit reached! You've used {current_usage:,} tokens this month. Please wait until next month or increase your limit.")
            return None, 0
        
        # Combine summary and answers
        context = f"Daily Summary: {summary}\n\nFollow-up Answers:\n{answers}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a skilled journaling assistant. Create natural, authentic journal entries that:
1. Sound like the user actually wrote them - conversational and personal
2. ONLY include details that were actually mentioned - NEVER assume or add things
3. Capture genuine emotions and thoughts - including negative ones
4. Are conversational and personal in tone
5. Include the date naturally
6. Keep it concise (300-400 words max)
7. Focus on the user's actual experience, not generic journaling
8. Don't force positivity - reflect the user's true feelings, even if negative
9. Don't assume positive outcomes - only state what the user actually said happened
10. Add reflective insights - help the user process their experience and gain self-awareness
11. Include personal growth moments - what they learned about themselves or the situation
12. Show emotional processing - how they're working through their feelings
13. Avoid formal structure - write naturally like a personal journal entry
14. Bridge gaps naturally - connect what they shared without adding assumptions"""
                },
                {
                    "role": "user",
                    "content": f"Using this daily summary and the user's answers to follow-up questions, write a natural, authentic journal entry. Write it like the person actually wrote it themselves - conversational, personal, and ONLY including what they actually shared. Don't force positivity or assume positive outcomes. Reflect their true feelings, even if negative. Add reflective insights and help them process their experience. Bridge gaps naturally without adding assumptions. Keep it concise and focused. Include today's date ({datetime.now().strftime('%B %d, %Y')}) naturally in the entry.\n\n{context}"
                }
            ],
            max_tokens=800,
            temperature=0.8
        )
        
        # Update token usage
        tokens_used = response.usage.total_tokens
        update_token_usage(tokens_used)
        
        return response.choices[0].message.content.strip(), tokens_used
    except Exception as e:
        st.error(f"Error generating journal entry: {str(e)}")
        return None, 0

def main():
    # Initialize OpenAI
    client = init_openai()
    
    # Initialize session state
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'journal_entry' not in st.session_state:
        st.session_state.journal_entry = None
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    if 'show_past_entries' not in st.session_state:
        st.session_state.show_past_entries = False
    if 'show_mood_tracker' not in st.session_state:
        st.session_state.show_mood_tracker = False
    if 'mood_before' not in st.session_state:
        st.session_state.mood_before = None
    if 'mood_after' not in st.session_state:
        st.session_state.mood_after = None
    if 'show_update_mood' not in st.session_state:
        st.session_state.show_update_mood = False
    
    # Show header only on home page (when no mode is selected and not in other views)
    if not st.session_state.mode and not st.session_state.show_past_entries and not st.session_state.show_mood_tracker:
            st.markdown('<h1 class="main-header">Smart Journal Assistant</h1>', unsafe_allow_html=True)
            
            # Center the subtitle using columns
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<p class="main-subtitle">Transform your rough daily summary into a thoughtful, reflective journal entry with AI assistance.</p>', unsafe_allow_html=True)
            
            # Create main content area with quote
            col_main, col_quote = st.columns([3, 1])
            
            with col_main:
                # Mode Selection
                st.markdown('<h2 class="section-header">Choose Your Journaling Mode</h2>', unsafe_allow_html=True)
                
                st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("### 🚀 Quick Mode")
                    st.markdown("**Perfect for:** Busy days, quick reflection")
                    st.markdown("**Process:** Summary + 3-4 questions → natural journal")
                    st.markdown("**Time:** ~30 seconds")
                    
                    if st.button("🚀 Start Quick Mode", type="primary", use_container_width=True):
                        st.session_state.mode = "quick"
                        st.rerun()
                
                with col_b:
                    st.markdown("### 📋 Detailed Mode")
                    st.markdown("**Perfect for:** Deep reflection, insights")
                    st.markdown("**Process:** Summary + 6-8 questions → deeper reflection")
                    st.markdown("**Time:** ~2-3 minutes")
                    
                    if st.button("📋 Start Detailed Mode", type="primary", use_container_width=True):
                        st.session_state.mode = "detailed"
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Mood tracking prompt
                st.markdown("### Track Your Mood")
                st.markdown("Before you start journaling, how are you feeling?")
                
                mood_before = mood_selection_ui()
                if mood_before:
                    # Save mood to mood data file
                    mood_data = load_mood_data()
                    today = datetime.now().strftime('%Y-%m-%d')
                    mood_data[today] = mood_before
                    save_mood_data(mood_data)
                    
                    st.session_state.mood_before = mood_before
                    st.success(f"Mood recorded: {get_mood_emoji(mood_before)} {mood_before.title()}")
                    
                    # Navigate to mood tracker page
                    st.session_state.show_mood_tracker = True
                    st.rerun()
            
            with col_quote:
                # Quote of the Day
                quote = get_quote_of_the_day()
                st.markdown("### Quote of the Day")
                st.markdown(f"**\"{quote['text']}\"**")
                st.markdown(f"*— {quote['author']}*")
                st.markdown("---")
    
    # Initialize OpenAI
    client = init_openai()
    
    # Sidebar for instructions
    with st.sidebar:
        st.markdown("### How it works:")
        st.markdown("1. **Choose your mode** - Quick or Detailed")
        st.markdown("2. **Share your day** - Write a rough summary")
        st.markdown("3. **Get your journal** - AI creates a polished entry")
        
        st.markdown("---")
        st.markdown("### Modes:")
        st.markdown("**Quick Mode:** Summary + 3-4 questions → natural journal")
        st.markdown("**Detailed Mode:** Summary + 6-8 questions → deeper reflection")
        
        st.markdown("---")
        st.markdown("### Tips for better results:")
        st.markdown("- Be honest and specific in your summary")
        st.markdown("- Include both positive and challenging moments")
        st.markdown("- Don't worry about perfect writing - just be real")
        
        st.markdown("---")
        st.markdown("### Past Entries")
        
        # Get analytics
        analytics = get_analytics()
        if analytics:
            st.markdown(f"**Total Entries:** {analytics.get('total_entries', 0)}")
            st.markdown(f"**This Week:** {analytics.get('recent_entries', 0)}")
            
            # Mode breakdown
            mode_stats = analytics.get('mode_stats', {})
            if mode_stats:
                st.markdown("**Mode Usage:**")
                for mode, count in mode_stats.items():
                    st.markdown(f"- {mode.title()}: {count}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Past Entries", use_container_width=True):
                st.session_state.show_past_entries = True
                st.session_state.show_mood_tracker = False
                st.rerun()
        with col2:
            if st.button("Mood Tracker", use_container_width=True):
                st.session_state.show_mood_tracker = True
                st.session_state.show_past_entries = False
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Past Entries View
        if st.session_state.show_past_entries:
            st.markdown('<h2 class="section-header">Your Journal History</h2>', unsafe_allow_html=True)
            
            # Search and filter options
            col_search, col_filter = st.columns(2)
            with col_search:
                search_term = st.text_input("Search entries:", placeholder="Enter keywords...")
            with col_filter:
                mode_filter = st.selectbox("Filter by mode:", ["All", "quick", "detailed"])
            
            # Get entries
            filter_mode = None if mode_filter == "All" else mode_filter
            entries = get_journal_entries(search_term=search_term, mode_filter=filter_mode)
            
            if entries:
                st.markdown(f"**Found {len(entries)} entries**")
                
                for entry in entries:
                    with st.expander(f"{entry['date']} - {entry['mode'].title()} Mode"):
                        st.markdown(f"**Summary:** {entry['summary']}")
                        st.markdown(f"**Journal Entry:**")
                        st.markdown(f"*{entry['journal_entry']}*")
                        
                        # Export button for this entry
                        entry_text = f"Journal Entry - {entry['date']}\n\nSummary: {entry['summary']}\n\nJournal Entry:\n{entry['journal_entry']}"
                        st.download_button(
                            label=f"Download {entry['date']}",
                            data=entry_text,
                            file_name=f"journal_entry_{entry['date']}.txt",
                            mime="text/plain",
                            key=f"download_{entry['id']}"
                        )
            else:
                st.info("No entries found. Start journaling to see your history here!")
            
            # Back to Journaling button
            st.markdown("---")
            if st.button("Back to Journaling", type="primary", use_container_width=True):
                st.session_state.show_past_entries = False
                st.session_state.show_mood_tracker = False
                st.rerun()
        
        # Mood Tracker View
        elif st.session_state.show_mood_tracker:
            st.markdown('<h2 class="section-header">Mood Tracker</h2>', unsafe_allow_html=True)
            
            # Load mood data
            mood_data = load_mood_data()
            
            # Calendar view
            st.subheader("Mood Calendar")
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            
            # Month navigation
            col_prev, col_current, col_next = st.columns(3)
            with col_prev:
                if st.button("◀ Previous Month", use_container_width=True):
                    if month == 1:
                        year -= 1
                        month = 12
                    else:
                        month -= 1
            with col_current:
                if st.button("Current Month", use_container_width=True):
                    year = current_date.year
                    month = current_date.month
            with col_next:
                if st.button("Next Month ▶", use_container_width=True):
                    if month == 12:
                        year += 1
                        month = 1
                    else:
                        month += 1
            
            # Display month/year header
            st.markdown(f"### {calendar.month_name[month]} {year}")
            
            # Display calendar
            calendar_html = create_mood_calendar(mood_data, year, month)
            st.markdown(calendar_html, unsafe_allow_html=True)
            
            # Mood selection for today
            st.subheader("Track Today's Mood")
            today = datetime.now().strftime('%Y-%m-%d')
            
            if today in mood_data:
                st.success(f"Mood recorded for today: {get_mood_emoji(mood_data[today])} {mood_data[today].title()}")
                if st.button("Update Today's Mood"):
                    st.session_state.mood_before = mood_data[today]
                    st.session_state.show_update_mood = True
                    st.rerun()
            else:
                selected_mood = mood_selection_ui()
                if selected_mood:
                    mood_data[today] = selected_mood
                    save_mood_data(mood_data)
                    st.success(f"Mood recorded: {get_mood_emoji(selected_mood)} {selected_mood.title()}")
                    st.rerun()
            
            # Show mood selection if updating
            if st.session_state.get('show_update_mood', False):
                st.markdown("**Select your new mood:**")
                new_mood = mood_selection_ui()
                if new_mood:
                    mood_data[today] = new_mood
                    save_mood_data(mood_data)
                    st.success(f"Mood updated: {get_mood_emoji(new_mood)} {new_mood.title()}")
                    st.session_state.show_update_mood = False
                    st.rerun()
            
            # Analytics
            mood_analytics_ui(mood_data)
            
            # Back to Journaling button
            st.markdown("---")
            if st.button("Back to Journaling", type="primary", use_container_width=True):
                st.session_state.show_past_entries = False
                st.session_state.show_mood_tracker = False
                st.rerun()
        

        
        # Journal Entry Process
        if st.session_state.mode:
            # Step 1: Daily Summary Input
            st.markdown(f'<h2 class="section-header">Step 1: Share Your Day ({st.session_state.mode.title()} Mode)</h2>', unsafe_allow_html=True)
            
            daily_summary = st.text_area(
                f"What happened today? (Share a rough summary of your day) - Max {500 if st.session_state.mode == 'quick' else 800} characters",
                height=150,
                placeholder="Today I... (write whatever comes to mind, no need to be perfect!)",
                help="Don't worry about perfect writing - just share what happened, how you felt, what stood out to you.",
                key="summary_input",
                max_chars=500 if st.session_state.mode == "quick" else 800
            )
            
            if st.session_state.mode == "quick":
                if st.button("Get Quick Questions", type="primary", disabled=not daily_summary.strip()):
                    with st.spinner("Generating quick questions..."):
                        questions = generate_quick_questions(client, daily_summary)
                        if questions:
                            st.session_state.questions = questions
                            st.session_state.step = 2
                            st.rerun()
                
                # Step 2: Quick Questions (Quick Mode)
                if st.session_state.questions and st.session_state.mode == "quick":
                    st.markdown('<h2 class="section-header">Step 2: Quick Reflection</h2>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="question-box">', unsafe_allow_html=True)
                    st.markdown("**Quick Questions:**")
                    st.markdown(st.session_state.questions)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Create text areas for answers
                    questions_list = st.session_state.questions.split('\n')
                    answers = []
                    
                    for i, question in enumerate(questions_list):
                        if question.strip():
                            answer = st.text_area(
                                f"Answer {i+1}:",
                                key=f"quick_answer_{i}",
                                height=80,
                                placeholder=f"Your quick answer to: {question.strip()}",
                                max_chars=200
                            )
                            answers.append(f"Q{i+1}: {question.strip()}\nA{i+1}: {answer}")
                    
                    if st.button("Generate Journal Entry", type="primary", disabled=not all(answers)):
                         with st.spinner("Creating your journal entry..."):
                             answers_text = "\n\n".join(answers)
                             journal_entry, tokens_used = generate_quick_journal_with_answers(client, daily_summary, answers_text)
                             if journal_entry:
                                 # Save to database
                                 save_journal_entry(
                                     mode="quick",
                                     summary=daily_summary,
                                     questions=st.session_state.questions,
                                     answers=answers_text,
                                     journal_entry=journal_entry,
                                     tokens_used=tokens_used
                                 )
                                 
                                 st.session_state.journal_entry = journal_entry
                                 st.session_state.step = 3
                                 st.rerun()
            
            elif st.session_state.mode == "detailed":
                if st.button("Ask AI for Follow-up Questions", type="primary", disabled=not daily_summary.strip()):
                    with st.spinner("Generating thoughtful questions..."):
                        questions = generate_follow_up_questions(client, daily_summary)
                        if questions:
                            st.session_state.questions = questions
                            st.session_state.step = 2
                            st.rerun()
                
                # Step 2: Follow-up Questions (Detailed Mode Only)
                if st.session_state.questions:
                    st.markdown('<h2 class="section-header">Step 2: Reflect Deeper</h2>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="question-box">', unsafe_allow_html=True)
                    st.markdown("**AI's Follow-up Questions:**")
                    st.markdown(st.session_state.questions)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Create text areas for answers
                    questions_list = st.session_state.questions.split('\n')
                    answers = []
                    
                    for i, question in enumerate(questions_list):
                        if question.strip():
                            answer = st.text_area(
                                f"Answer {i+1}:",
                                key=f"answer_{i}",
                                height=100,
                                placeholder=f"Your answer to: {question.strip()}",
                                max_chars=300
                            )
                            answers.append(f"Q{i+1}: {question.strip()}\nA{i+1}: {answer}")
                    
                    if st.button("Generate Journal Entry", type="primary", disabled=not all(answers)):
                        with st.spinner("Creating your reflective journal entry..."):
                            answers_text = "\n\n".join(answers)
                            journal_entry, tokens_used = generate_journal_entry(client, daily_summary, answers_text)
                            if journal_entry:
                                # Save to database
                                save_journal_entry(
                                    mode="detailed",
                                    summary=daily_summary,
                                    questions=st.session_state.questions,
                                    answers=answers_text,
                                    journal_entry=journal_entry,
                                    tokens_used=tokens_used
                                )
                                
                                st.session_state.journal_entry = journal_entry
                                st.session_state.step = 3
                                st.rerun()
    
    if st.session_state.mode:
        with col2:
            # Display current step and progress
            st.markdown("### Progress")
            
            if st.session_state.mode == "quick":
                steps = ["Share Your Day", "Quick Questions", "Get Journal Entry"]
                for i, step in enumerate(steps, 1):
                    if i <= st.session_state.step:
                        st.markdown(f'<div class="progress-step active">{step}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="progress-step">{step}</div>', unsafe_allow_html=True)
            else:
                steps = ["Share Your Day", "Answer Questions", "Get Journal Entry"]
                for i, step in enumerate(steps, 1):
                    if i <= st.session_state.step:
                        st.markdown(f'<div class="progress-step active">{step}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="progress-step">{step}</div>', unsafe_allow_html=True)
            
            # Display the final journal entry
            if st.session_state.journal_entry:
                st.markdown('<h2 class="section-header">Your Journal Entry</h2>', unsafe_allow_html=True)
                st.markdown('<div class="journal-entry">', unsafe_allow_html=True)
                st.markdown(st.session_state.journal_entry)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Mood tracking after journaling
                st.markdown("---")
                st.markdown("### How do you feel now?")
                st.markdown("After journaling, has your mood changed?")
                
                mood_after = mood_selection_ui()
                if mood_after:
                    st.session_state.mood_after = mood_after
                    
                    # Save mood data
                    mood_data = load_mood_data()
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    # Save before and after moods
                    if st.session_state.mood_before:
                        mood_data[f"{today}_before"] = st.session_state.mood_before
                    mood_data[f"{today}_after"] = mood_after
                    save_mood_data(mood_data)
                    
                    st.success(f"Mood tracked: {get_mood_emoji(mood_after)} {mood_after.title()}")
                    
                    # Show mood change
                    if st.session_state.mood_before and st.session_state.mood_before != mood_after:
                        st.info(f"Mood change: {get_mood_emoji(st.session_state.mood_before)} {st.session_state.mood_before.title()} → {get_mood_emoji(mood_after)} {mood_after.title()}")
                
                # Download button
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                journal_text = f"Smart Journal Entry - {timestamp}\n\n{st.session_state.journal_entry}"
                st.download_button(
                    label="Download Journal Entry",
                    data=journal_text,
                    file_name=f"journal_entry_{timestamp}.txt",
                    mime="text/plain",
                    key="download_current_entry"
                )
                
                # Reset button
                if st.button("Start New Entry"):
                    st.session_state.clear()
                    st.rerun()
                
                # Change mode button
                if st.button("Change Mode"):
                    st.session_state.mode = None
                    st.rerun()

if __name__ == "__main__":
    main() 