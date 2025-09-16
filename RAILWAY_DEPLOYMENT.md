# 🚂 Railway Deployment Guide

## Quick Start (5 minutes)

### Step 1: Sign Up
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub
4. Authorize Railway to access your repositories

### Step 2: Deploy Your App
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `SmartJournalV2` repository
4. Railway will auto-detect it's a Python app
5. Click "Deploy"

### Step 3: Add PostgreSQL Database
1. In your project dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway creates the database automatically
4. The `DATABASE_URL` environment variable is set automatically

### Step 4: Set Environment Variables
1. Go to your app's settings
2. Click "Variables" tab
3. Add these variables:

```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=your-jwt-secret-key
```

**Generate secrets:**
- `SECRET_KEY`: Use the deploy.py script or generate a random string
- `OPENAI_API_KEY`: Get from [platform.openai.com](https://platform.openai.com/api-keys)
- `JWT_SECRET_KEY`: Generate another random string

### Step 5: Deploy!
1. Railway automatically redeploys when you push to GitHub
2. Your app will be available at `https://yourapp.railway.app`
3. Database migrations run automatically

## 🎯 What Happens:

1. **Railway detects** your Python app
2. **Installs dependencies** from requirements.txt
3. **Runs your app** using run.py
4. **Creates PostgreSQL database** automatically
5. **Sets DATABASE_URL** environment variable
6. **Deploys** to a public URL

## 💰 Cost:
- **Free tier**: $5 credit monthly (usually enough for small apps)
- **Database**: Included in free tier
- **Custom domain**: Available for $2/month

## 🔧 Troubleshooting:

### App won't start:
- Check the "Deployments" tab for error logs
- Ensure all environment variables are set
- Verify requirements.txt includes all dependencies

### Database issues:
- Check that PostgreSQL service is running
- Verify DATABASE_URL is set correctly
- Run migrations: Railway handles this automatically

### Environment variables:
- Make sure SECRET_KEY and OPENAI_API_KEY are set
- Check for typos in variable names
- Restart deployment after adding variables

## 🚀 Next Steps:

1. **Test your app** at the Railway URL
2. **Add a custom domain** (optional)
3. **Set up monitoring** (optional)
4. **Configure backups** (automatic with Railway)

## 📞 Support:
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Community: [discord.gg/railway](https://discord.gg/railway)
