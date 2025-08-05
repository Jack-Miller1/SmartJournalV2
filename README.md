# 📝 Smart Journal Assistant

A secure, AI-powered journaling app that helps you transform rough daily summaries into thoughtful, reflective journal entries.

## 🔐 Security Features

- **Environment Variables:** API keys stored securely in environment variables
- **Local Database:** All journal entries stored locally on your machine
- **No Cross-User Data:** Each user only sees their own entries
- **Secure Input:** API key input is masked and not stored permanently

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit openai
```

### 2. Set Up API Key (Choose One Method)

#### Method A: Environment Variables (Recommended)
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
TOKEN_LIMIT=40000
```

#### Method B: Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your_actual_api_key_here"
TOKEN_LIMIT = 40000
```

#### Method C: In-App Input
The app will prompt you to enter your API key securely if not found in environment variables.

### 3. Run the App
```bash
streamlit run smart_journal.py
```

## 🛡️ Security Best Practices

1. **Never commit your API key** - The `.gitignore` file prevents accidental commits
2. **Use environment variables** - Most secure for production deployment
3. **Local storage only** - Your journal entries stay on your machine
4. **No user tracking** - No analytics or data collection

## 📊 Features

- **Two Journaling Modes:** Quick (3-4 questions) and Detailed (6-8 questions)
- **Natural AI Output:** Authentic, conversational journal entries
- **Search & Filter:** Find past entries by keywords or mode
- **Export Functionality:** Download entries as text files
- **Usage Analytics:** Track token usage and journaling patterns
- **Character Limits:** Prevent token abuse with input limits

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `TOKEN_LIMIT`: Monthly token usage limit (default: 40000)

### Database
- Journal entries stored in `journal_entries.db`
- Token usage tracked in `token_usage.json`
- Both files are local and private

## 📝 Usage

1. **Choose Mode:** Quick for busy days, Detailed for deep reflection
2. **Share Your Day:** Write a rough summary of your day
3. **Answer Questions:** Respond to AI-generated follow-up questions
4. **Get Journal Entry:** Receive a natural, reflective journal entry
5. **View History:** Search and browse past entries
6. **Export:** Download entries as text files

## 🛠️ Development

### File Structure
```
smart_journal_assistant/
├── smart_journal.py      # Main application
├── .env.example         # Environment variables template
├── .gitignore          # Prevents committing sensitive files
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

### Security Files (Not Committed)
- `.env` - Your actual environment variables
- `journal_entries.db` - Your journal entries database
- `token_usage.json` - Token usage tracking
- `.streamlit/secrets.toml` - Streamlit secrets (if used)

## 🤝 Contributing

This is a personal project focused on security and privacy. All data stays local to your machine.

## 📄 License

Personal use only. Keep your journal entries private and secure. 