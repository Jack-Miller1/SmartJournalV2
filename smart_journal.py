import streamlit as st
import openai
import os
import sqlite3
from datetime import datetime
import json

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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .journal-entry {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .question-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .mode-selector {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 2px solid #1f77b4;
    }
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
    # Header
    st.markdown('<h1 class="main-header">📝 Smart Journal Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Transform your rough daily summary into a thoughtful, reflective journal entry with AI assistance.")
    
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
    
    # Sidebar for instructions
    with st.sidebar:
        st.markdown("### 📋 How it works:")
        st.markdown("1. **Choose your mode** - Quick or Detailed")
        st.markdown("2. **Share your day** - Write a rough summary")
        st.markdown("3. **Get your journal** - AI creates a polished entry")
        
        st.markdown("---")
        st.markdown("### 🚀 Modes:")
        st.markdown("**Quick Mode:** Summary + 3-4 questions → natural journal")
        st.markdown("**Detailed Mode:** Summary + 6-8 questions → deeper reflection")
        
        st.markdown("---")
        st.markdown("### 💡 Tips for better results:")
        st.markdown("- Be honest and specific in your summary")
        st.markdown("- Include both positive and challenging moments")
        st.markdown("- Don't worry about perfect writing - just be real")
        
        st.markdown("---")
        st.markdown("### 📊 Token Usage")
        within_limit, current_usage = check_token_limit()
        limit = st.secrets.get("TOKEN_LIMIT", 40000)
        
        # Create progress bar for token usage
        usage_percentage = (current_usage / limit) * 100
        st.progress(usage_percentage / 100)
        st.markdown(f"**Used:** {current_usage:,} / {limit:,} tokens")
        
        if within_limit:
            st.markdown(f"**Remaining:** {limit - current_usage:,} tokens")
        else:
            st.error("⚠️ Token limit reached!")
        
        st.markdown(f"**This month:** {datetime.now().strftime('%B %Y')}")
        
        st.markdown("---")
        st.markdown("### 📚 Past Entries")
        
        # Get analytics
        analytics = get_analytics()
        if analytics:
            st.markdown(f"**Total Entries:** {analytics.get('total_entries', 0)}")
            st.markdown(f"**This Week:** {analytics.get('recent_entries', 0)}")
            st.markdown(f"**Total Tokens:** {analytics.get('total_tokens', 0):,}")
            
            # Mode breakdown
            mode_stats = analytics.get('mode_stats', {})
            if mode_stats:
                st.markdown("**Mode Usage:**")
                for mode, count in mode_stats.items():
                    st.markdown(f"- {mode.title()}: {count}")
        
        # View past entries button
        if st.button("📖 View Past Entries", use_container_width=True):
            st.session_state.show_past_entries = True
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Past Entries View
        if st.session_state.show_past_entries:
            st.markdown('<h2 class="section-header">📚 Your Journal History</h2>', unsafe_allow_html=True)
            
            # Search and filter options
            col_search, col_filter = st.columns(2)
            with col_search:
                search_term = st.text_input("🔍 Search entries:", placeholder="Enter keywords...")
            with col_filter:
                mode_filter = st.selectbox("📊 Filter by mode:", ["All", "quick", "detailed"])
            
            # Get entries
            filter_mode = None if mode_filter == "All" else mode_filter
            entries = get_journal_entries(search_term=search_term, mode_filter=filter_mode)
            
            if entries:
                st.markdown(f"**Found {len(entries)} entries**")
                
                for entry in entries:
                    with st.expander(f"📝 {entry['date']} - {entry['mode'].title()} Mode"):
                        st.markdown(f"**Summary:** {entry['summary']}")
                        st.markdown(f"**Journal Entry:**")
                        st.markdown(f"*{entry['journal_entry']}*")
                        
                        # Export button for this entry
                        entry_text = f"Journal Entry - {entry['date']}\n\nSummary: {entry['summary']}\n\nJournal Entry:\n{entry['journal_entry']}"
                        st.download_button(
                            label=f"📥 Download {entry['date']}",
                            data=entry_text,
                            file_name=f"journal_entry_{entry['date']}.txt",
                            mime="text/plain",
                            key=f"download_{entry['id']}"
                        )
            else:
                st.info("No entries found. Start journaling to see your history here!")
            
            if st.button("🔄 Back to Journaling"):
                st.session_state.show_past_entries = False
                st.rerun()
        
        # Mode Selection
        elif not st.session_state.mode:
            st.markdown('<h2 class="section-header">Choose Your Journaling Mode</h2>', unsafe_allow_html=True)
            
            st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("### ⚡ Quick Mode")
                st.markdown("**Perfect for:** Busy days, quick reflection")
                st.markdown("**Process:** Summary + 3-4 questions → natural journal")
                st.markdown("**Time:** ~30 seconds")
                st.markdown("**Cost:** ~$0.001 per entry")
                
                if st.button("🚀 Start Quick Mode", type="primary", use_container_width=True):
                    st.session_state.mode = "quick"
                    st.rerun()
            
            with col_b:
                st.markdown("### 🧠 Detailed Mode")
                st.markdown("**Perfect for:** Deep reflection, insights")
                st.markdown("**Process:** Summary + 6-8 questions → deeper reflection")
                st.markdown("**Time:** ~2-3 minutes")
                st.markdown("**Cost:** ~$0.002 per entry")
                
                if st.button("🧠 Start Detailed Mode", type="primary", use_container_width=True):
                    st.session_state.mode = "detailed"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
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
                if st.button("🤔 Get Quick Questions", type="primary", disabled=not daily_summary.strip()):
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
                    
                    if st.button("📝 Generate Journal Entry", type="primary", disabled=not all(answers)):
                         with st.spinner("Creating your journal entry..."):
                             answers_text = "\n\n".join(answers)
                             journal_entry, tokens_used = generate_quick_journal_with_answers(client, daily_summary, answers_text)
                             if journal_entry:
                                 # Save to database
                                 save_success = save_journal_entry(
                                     mode="quick",
                                     summary=daily_summary,
                                     questions=st.session_state.questions,
                                     answers=answers_text,
                                     journal_entry=journal_entry,
                                     tokens_used=tokens_used
                                 )
                                 
                                 if save_success:
                                     st.success("✅ Journal entry saved!")
                                 
                                 st.session_state.journal_entry = journal_entry
                                 st.session_state.step = 3
                                 st.rerun()
            
            elif st.session_state.mode == "detailed":
                if st.button("🤔 Ask AI for Follow-up Questions", type="primary", disabled=not daily_summary.strip()):
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
                    
                    if st.button("📝 Generate Journal Entry", type="primary", disabled=not all(answers)):
                        with st.spinner("Creating your reflective journal entry..."):
                            answers_text = "\n\n".join(answers)
                            journal_entry, tokens_used = generate_journal_entry(client, daily_summary, answers_text)
                            if journal_entry:
                                # Save to database
                                save_success = save_journal_entry(
                                    mode="detailed",
                                    summary=daily_summary,
                                    questions=st.session_state.questions,
                                    answers=answers_text,
                                    journal_entry=journal_entry,
                                    tokens_used=tokens_used
                                )
                                
                                if save_success:
                                    st.success("✅ Journal entry saved!")
                                
                                st.session_state.journal_entry = journal_entry
                                st.session_state.step = 3
                                st.rerun()
    
    with col2:
        # Display current step and progress
        st.markdown("### 📊 Progress")
        
        if st.session_state.mode == "quick":
            steps = ["Share Your Day", "Quick Questions", "Get Journal Entry"]
            for i, step in enumerate(steps, 1):
                if i <= st.session_state.step:
                    st.markdown(f"✅ **{step}**")
                else:
                    st.markdown(f"⏳ {step}")
        else:
            steps = ["Share Your Day", "Answer Questions", "Get Journal Entry"]
            for i, step in enumerate(steps, 1):
                if i <= st.session_state.step:
                    st.markdown(f"✅ **{step}**")
                else:
                    st.markdown(f"⏳ {step}")
        
        # Display the final journal entry
        if st.session_state.journal_entry:
            st.markdown('<h2 class="section-header">Your Journal Entry</h2>', unsafe_allow_html=True)
            st.markdown('<div class="journal-entry">', unsafe_allow_html=True)
            st.markdown(st.session_state.journal_entry)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            journal_text = f"Smart Journal Entry - {timestamp}\n\n{st.session_state.journal_entry}"
            st.download_button(
                label="📥 Download Journal Entry",
                data=journal_text,
                file_name=f"journal_entry_{timestamp}.txt",
                mime="text/plain",
                key="download_current_entry"
            )
            
            # Reset button
            if st.button("🔄 Start New Entry"):
                st.session_state.clear()
                st.rerun()
            
            # Change mode button
            if st.button("🔄 Change Mode"):
                st.session_state.mode = None
                st.rerun()

if __name__ == "__main__":
    main() 