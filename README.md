# 📖 MindFlow

A modern, AI-powered journaling application built with Flask that helps you reflect on your daily experiences and track your emotional journey.

## ✨ Features

### 🔐 **Authentication System**
- Secure user registration and login
- JWT-based authentication
- Role-based access control
- Password hashing with SHA-256

### 📝 **Journaling Modes**
- **Quick Mode**: Fast reflection with basic prompts
- **Detailed Mode**: In-depth reflection with AI-generated questions (coming soon)

### 😊 **Mood Tracking**
- Before and after journaling mood assessment
- Visual mood patterns over time
- Emotional journey insights

### 🎨 **Modern UI/UX**
- Responsive design with Bootstrap 5
- Beautiful gradient backgrounds
- Interactive mood selection
- Smooth animations and transitions

### 📊 **Analytics & Insights**
- Journal entry statistics
- Mood tracking visualization
- Personal growth metrics
- Export functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MindFlow.git
cd MindFlow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Default admin account: `admin` / `admin123`

## 🏗️ Architecture

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Flask-Login with JWT support
- **Database Migrations**: Flask-Migrate

### Frontend
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Inter)
- **JavaScript**: Vanilla JS with modern ES6+ features

### Database Schema
- **Users**: Authentication and profile data
- **Journal Entries**: Daily reflections and insights
- **Mood Entries**: Emotional tracking data

## 🌐 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment options:
- Heroku (recommended for beginners)
- Python Anywhere (free hosting)
- DigitalOcean App Platform
- AWS/GCP/Azure (enterprise)

## 🔧 Configuration

### Environment Variables
```bash
# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Flask Environment
FLASK_ENV=production
```

## 📱 Features in Detail

### Journal Entry Creation
1. **Choose Mode**: Quick or detailed journaling
2. **Daily Summary**: Describe your day's events
3. **Mood Check**: Track how you're feeling
4. **Reflection**: Write your thoughts and insights
5. **Save & Review**: Store and revisit your entries

### Dashboard Overview
- Recent journal entries
- Quick action buttons
- Mood tracking statistics
- Personal insights

### Profile Management
- Account information
- Journaling statistics
- Recent activity
- Account settings

## 🔒 Security Features

- **Password Hashing**: SHA-256 with salt
- **Session Management**: Secure cookie handling
- **CSRF Protection**: Built-in Flask security
- **Input Validation**: Form sanitization
- **SQL Injection Protection**: ORM-based queries

## 🚧 Roadmap

### Phase 1 (Current)
- ✅ User authentication system
- ✅ Basic journaling functionality
- ✅ Mood tracking
- ✅ Modern responsive UI

### Phase 2 (Next)
- 🤖 AI-powered question generation
- 📊 Advanced analytics and charts
- 📧 Email notifications
- 🔄 Data import/export

### Phase 3 (Future)
- 📱 Mobile app
- 👥 Social features
- 🎯 Goal tracking
- 🧠 Machine learning insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask** - The web framework for Python
- **Bootstrap** - The most popular CSS framework
- **Font Awesome** - The icon toolkit
- **OpenAI** - AI-powered insights (coming soon)

## 📞 Support

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Smart-Journal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Smart-Journal/discussions)

---

**Built with ❤️ for mindful reflection and personal growth**

Start your journaling journey today! 🚀 