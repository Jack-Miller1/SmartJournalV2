# Smart Journal (MindFlow) - Features Overview

## 🚀 Core Features

### **User Management**
- ✅ User registration and authentication
- ✅ Secure password hashing
- ✅ User profiles with statistics
- ✅ Session management

### **Journaling System**
- ✅ Quick and detailed journal modes
- ✅ AI-powered reflection questions
- ✅ Daily mood tracking (before/after journaling)
- ✅ Journal entry management and viewing
- ✅ Entry download functionality

### **AI Integration**
- ✅ OpenAI GPT-3.5-turbo integration
- ✅ Dynamic reflection question generation
- ✅ Journal entry enhancement with AI insights
- ✅ Fallback mechanisms when AI is unavailable

### **Mood Analytics**
- ✅ Interactive mood trend charts
- ✅ Mood distribution visualization
- ✅ Before vs. after journaling comparison
- ✅ Date range filtering (7 days to 1 year)
- ✅ Multiple chart types (line, bar, area)
- ✅ Mood improvement tracking

### **Database Management**
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Database viewer and manager tools
- ✅ Interactive database exploration
- ✅ Custom query execution

## 🛠️ Technical Stack

### **Backend**
- **Framework**: Flask 2.3.0+
- **Database**: SQLite with SQLAlchemy
- **Authentication**: Flask-Login
- **AI**: OpenAI API integration
- **Language**: Python 3.x

### **Frontend**
- **Templates**: Jinja2 with Bootstrap 5.3.0
- **Charts**: Plotly.js for data visualization
- **Icons**: Font Awesome 6.4.0
- **Styling**: Custom CSS with modern design
- **JavaScript**: Vanilla JS with AJAX

### **Database Models**
- **User**: Authentication and profile data
- **JournalEntry**: Journal content and metadata
- **MoodEntry**: Mood tracking data

## 📊 Analytics Features

### **Mood Tracking**
- Real-time mood recording
- Before/after journaling comparison
- Mood trend analysis over time
- Mood distribution charts
- Improvement rate calculation

### **Journal Statistics**
- Entry count by mode (quick/detailed)
- Writing frequency tracking
- AI token usage monitoring
- User activity patterns

## 🔧 Development Tools

### **Database Management**
- `db_viewer.py` - Quick database overview
- `db_manager.py` - Interactive database manager
- `setup_env.py` - Environment configuration setup

### **Configuration**
- Environment variable management
- Secure key generation
- Development/production settings
- OpenAI API configuration

## 🚀 Getting Started

1. **Setup Environment**
   ```bash
   python setup_env.py
   # Edit .env file with your OpenAI API key
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   python run.py
   ```

4. **Access Application**
   - URL: http://localhost:5000
   - Default admin: admin/admin123

## 📱 User Interface

### **Responsive Design**
- Mobile-friendly interface
- Bootstrap 5 responsive grid
- Modern glassmorphism design
- Smooth animations and transitions

### **Interactive Elements**
- Dynamic form validation
- Real-time AJAX updates
- Interactive charts and graphs
- Responsive data tables

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management
- CSRF protection
- Secure cookie settings
- User authentication middleware

## 📈 Future Enhancements

- Export functionality (PDF, CSV)
- Advanced analytics and insights
- Social features and sharing
- Mobile app development
- Additional AI models integration

## 🐛 Troubleshooting

### **Common Issues**
- Database connection errors
- OpenAI API key configuration
- Chart rendering issues
- JavaScript console errors

### **Debug Tools**
- Flask debug mode
- Database viewer scripts
- Browser developer tools
- Console logging

---

**Smart Journal** - Your AI-powered personal reflection companion
