# 🚀 QUICK START GUIDE
**AI Recruitment Assistant**

---

## ✅ System Status

Your application has been **fully tested and verified**! All features are working correctly.

**Test Results**: 7/7 tests passed ✓
- Database: ✓ Connected
- Backend API: ✓ Running  
- Authentication: ✓ Working
- All Features: ✓ Functional

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Start the Backend Server

Open PowerShell and run:

```powershell
cd c:\Users\supri\ai-recruit-assistant
.\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**✓ Server is now running at http://localhost:8000**

---

### Step 2: Open the Frontend

**Option A: Direct File Access**
- Open `frontend/register.html` in your browser
- Or `frontend/login.html` if you already have an account

**Option B: Using Local Server (Recommended)**

Open a NEW PowerShell window:

```powershell
cd c:\Users\supri\ai-recruit-assistant\frontend
python -m http.server 5500
```

Then open: http://localhost:5500/register.html

---

### Step 3: Create Your Admin Account

1. Fill in the registration form:
   - **Name**: Your Full Name
   - **Email**: your.email@example.com
   - **Password**: Choose a secure password (min 6 characters)
   - **Role**: Select "Admin" (gives you full access)

2. Click **"Create Account"**

3. You'll be automatically logged in and redirected to the dashboard!

---

## 🎮 Using the Application

### Main Features

#### 1. **Candidates** 📋
- **Upload Resumes**: Drag & drop PDF files or click to browse
- **View Profiles**: Click on any candidate to see details
- **Search**: Filter candidates by name or email
- The system automatically parses resume data using AI

#### 2. **Jobs** 💼
- **Create Job Postings**: Click "Create New Job"
- **Fill in Details**: Job title and description
- **View All Jobs**: See all active job postings
- **Edit/Delete**: Manage job listings

#### 3. **Interviews** 📅
- **Schedule Interviews**: Link candidates with jobs
- **Add Notes**: Track interview feedback
- **Filter**: View upcoming, past, or all interviews
- **Update Status**: Mark interviews as completed

#### 4. **Ranking** ⭐
- **Compare Candidates**: Rank candidates against job requirements
- **AI Scoring**: Uses AI to analyze fit (requires OpenAI key)
- **View Results**: See detailed ranking breakdown

#### 5. **AI Tools** 🤖

**Generate Interview Questions**
- Select job and candidate
- Choose difficulty level
- Get personalized questions
- Copy to clipboard

**Analyze Feedback**
- Add interview notes
- Get AI analysis of candidate performance
- Identify strengths and areas for improvement

**Optimize Resume**
- Upload candidate resume
- Get AI-powered optimization suggestions
- Improve resume quality

---

## ⚙️ Configuration

### Required: OpenAI API Key (For AI Features)

To enable AI features, you need an OpenAI API key:

1. Get an API key from: https://platform.openai.com/api-keys

2. Open `backend\.env` file

3. Replace this line:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```
   
   With your actual key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   ```

4. Restart the backend server

**Without OpenAI Key**: All other features work perfectly! Only AI-specific features (question generation, feedback analysis, resume optimization) will be unavailable.

---

## 🔐 User Roles

Your system supports 3 role types:

### Admin (Full Access) ✓
- All features available
- User management
- Full CRUD operations

### Recruiter
- Upload candidates
- Create jobs
- Schedule interviews
- Rank candidates
- Use AI tools

### Interviewer
- View candidates and jobs
- Conduct interviews
- Add interview notes
- Use AI question generator

---

## 📊 What's Already in the Database

Your system already has sample data:
- **3 Users** (including test accounts)
- **2 Candidates** 
- **2 Jobs**
- **1 Interview**

You can view and manage all of these from the dashboard!

---

## 🛠️ Common Tasks

### Add a Candidate
1. Go to **Candidates** section
2. Click **"Upload Resume"**
3. Drag & drop a PDF file
4. System automatically parses the resume
5. View parsed data in candidate profile

### Create a Job Posting
1. Go to **Jobs** section
2. Click **"Create New Job"**
3. Enter title and description
4. Click **"Create Job"**

### Schedule an Interview
1. Go to **Interviews** section
2. Click **"Schedule Interview"**
3. Select candidate from dropdown
4. Select job from dropdown
5. Choose date/time
6. Add interviewer name
7. Click **"Schedule"**

### Rank a Candidate
1. Go to **Ranking** section
2. Select a job
3. Select a candidate
4. Click **"Rank Candidate"**
5. View AI-generated score and details

---

## 🐛 Troubleshooting

### Server Won't Start
```powershell
# Kill any existing Python processes
Stop-Process -Name python -Force -ErrorAction SilentlyContinue

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start fresh
cd c:\Users\supri\ai-recruit-assistant
.\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### "Login Required" Error
- Make sure you're registered
- Check that you're using the correct email/password
- Try registering a new account

### AI Features Not Working
- Check if OpenAI API key is set in `.env`
- Verify the key is valid
- Check backend logs for specific errors
- Ensure you have OpenAI credits

### Database Errors
```powershell
# Test database connection
cd c:\Users\supri\ai-recruit-assistant
.\venv\Scripts\Activate.ps1
python backend\test_db.py
```

---

## 📝 Test Accounts

You can create test users with these roles:

```
Admin Account:
- Email: admin@yourcompany.com
- Password: admin123
- Role: admin

Recruiter Account:
- Email: recruiter@yourcompany.com
- Password: recruiter123
- Role: recruiter

Interviewer Account:
- Email: interviewer@yourcompany.com
- Password: interviewer123
- Role: interviewer
```

---

## 🔍 API Documentation

Backend API is available at:
- **Base URL**: http://localhost:8000/api/v1
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

**Register User:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"pass123","role":"admin"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'
```

**Get Candidates (with auth):**
```bash
curl http://localhost:8000/api/v1/candidates \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📚 Documentation

Full documentation is available in:
- `SYSTEM_ANALYSIS_REPORT.md` - Complete system analysis
- `README.md` - Project overview
- Backend API Docs: http://localhost:8000/docs

---

## ✨ Tips for Best Experience

1. **Use Chrome or Firefox** for best compatibility
2. **Keep backend server running** while using the app
3. **Check browser console** (F12) if you encounter issues
4. **Set OpenAI API key** to unlock all AI features
5. **Create admin account first** for full access
6. **Test with sample data** before using real resumes

---

## 🎉 You're All Set!

Your AI Recruitment Assistant is ready to use!

**Next Steps:**
1. ✅ Start the backend server
2. ✅ Open the frontend
3. ✅ Create your admin account
4. ✅ Start managing your recruitment process!

**Need Help?**
- Check `SYSTEM_ANALYSIS_REPORT.md` for detailed technical info
- Review backend logs for API errors
- Check browser console for frontend issues

---

**Happy Recruiting! 🚀**
