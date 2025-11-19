# Quick Start Guide - AI Recruitment Assistant with Authentication

## Prerequisites
- PostgreSQL 18 installed and running
- Python virtual environment activated
- All dependencies installed

## Step-by-Step Setup

### 1. Start Backend Server
```powershell
# Navigate to project
cd c:\Users\supri\ai-recruit-assistant

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Go to backend folder
cd backend

# Start the server
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Starting AI Recruitment Assistant API
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Open Frontend

Open your browser and navigate to:
```
file:///c:/Users/supri/ai-recruit-assistant/frontend/login.html
```

Or simply double-click `frontend/login.html`

### 3. Create Your First Account

1. Click "Create one" link on login page
2. Fill in the registration form:
   - **Name:** Your Full Name
   - **Email:** your.email@example.com
   - **Password:** At least 6 characters
   - **Role:** Select "admin" for first user (has all permissions)
3. Click "Create Account"
4. You'll be automatically logged in and redirected to the dashboard!

### 4. Start Using the Platform

Now you can:
- ✅ Upload candidate resumes
- ✅ Create job postings
- ✅ Schedule interviews
- ✅ Rank candidates with AI
- ✅ Generate interview questions
- ✅ Analyze interview feedback
- ✅ Optimize resumes for ATS

### 5. Create Additional Users

To create team members:
1. Click your name in the top right
2. Logout
3. Go to register page
4. Create new account with appropriate role:
   - **Admin:** Full access
   - **Recruiter:** Can manage candidates, jobs, interviews
   - **Interviewer:** Can view/conduct interviews, limited editing

### 6. Test the Features

**Upload a Candidate:**
1. Go to Candidates section
2. Click "Upload Resume"
3. Fill in name, email, phone
4. Select PDF or DOCX resume file
5. Click Upload
6. Resume will be parsed automatically!

**Create a Job:**
1. Go to Jobs section
2. Click "Create Job"
3. Enter job title and description
4. Click Create

**Schedule an Interview:**
1. Go to Interviews section
2. Click "Schedule Interview"
3. Select candidate and job
4. Choose date/time
5. Add interviewer name and notes
6. Click Schedule

**Rank a Candidate:**
1. Go to Ranking section
2. Select a job from dropdown
3. Select a candidate
4. Click "Rank Candidate"
5. AI will analyze and provide score!

**Generate Interview Questions:**
1. Go to any interview
2. Click "Generate Questions"
3. Select job and candidate
4. Choose number of questions
5. Select difficulty
6. AI generates personalized questions!

**Analyze Interview Feedback:**
1. Find an interview
2. Click "Analyze Feedback"
3. Enter interview notes
4. AI provides structured analysis with hire recommendation!

**Optimize Resume:**
1. Go to candidate detail
2. Click "Optimize Resume"
3. Get ATS score and improvement suggestions!

## API Documentation

Access interactive API docs at:
```
http://127.0.0.1:8000/api/v1/docs
```

Here you can:
- See all available endpoints
- Test endpoints directly
- View request/response schemas
- Try authentication

### Testing with Swagger UI

1. Click "Authorize" button (top right)
2. Get your token from localStorage or login first
3. Enter: `Bearer <your_token>`
4. Click "Authorize"
5. Now you can test all protected endpoints!

## Troubleshooting

### Server Won't Start
```powershell
# Check if Python is in venv
which python
# Should show: C:\Users\supri\ai-recruit-assistant\venv\Scripts\python.exe

# Check if dependencies installed
pip list | findstr uvicorn
pip list | findstr fastapi
pip list | findstr PyJWT
```

### Database Connection Error
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# Test database exists
psql -U postgres -l | findstr ai_recruitment
```

### Login Not Working
1. Check browser console (F12) for errors
2. Verify backend is running (http://127.0.0.1:8000/api/v1/health)
3. Check network tab for API responses
4. Ensure localStorage has space (not full)

### "Session expired" Error
1. Check your system time is correct
2. Token expires after 30 minutes - just login again
3. Check SECRET_KEY in .env file exists

### "You do not have permission"
1. Check your role in user menu
2. Only recruiters/admins can upload candidates
3. Only interviewers+ can view interviews
4. Create admin account for full access

## User Roles & Permissions

### Admin
- ✅ Everything

### Recruiter
- ✅ Upload/manage candidates
- ✅ Create/manage jobs
- ✅ Schedule/manage interviews
- ✅ Rank candidates
- ✅ Use all AI tools
- ❌ Cannot manage other admins

### Interviewer
- ✅ View interviews
- ✅ Add interview notes
- ✅ Generate questions
- ✅ Analyze feedback
- ❌ Cannot upload candidates
- ❌ Cannot create jobs
- ❌ Cannot schedule interviews

## Tips & Best Practices

1. **Create admin account first** - Gives you full access to set up the system

2. **Use strong passwords** - Minimum 6 characters, but longer is better

3. **Assign appropriate roles** - Don't make everyone admin

4. **Logout when done** - Especially on shared computers

5. **Keep backend running** - Frontend needs API server to work

6. **Check logs** - Backend terminal shows useful debug info

7. **Use HTTPS in production** - Current setup is for development only

## Next Steps

1. ✅ Create your admin account
2. ✅ Upload some test candidates
3. ✅ Create job postings
4. ✅ Schedule interviews
5. ✅ Try AI features (questions, feedback, optimization)
6. ✅ Create team member accounts
7. ✅ Start recruiting!

## Need Help?

- Check `PHASE4_COMPLETE.md` for detailed documentation
- View API docs at `/api/v1/docs`
- Check browser console for frontend errors
- Check backend terminal for API errors

---

**Congratulations! You're ready to use the AI Recruitment Assistant!** 🎉
