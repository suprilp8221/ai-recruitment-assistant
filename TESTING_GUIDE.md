# AI Recruitment Assistant - Testing Guide

## Prerequisites
- PostgreSQL database running with `ai_recruit` database created
- Virtual environment activated
- All dependencies installed (`pip install -r backend/requirements.txt`)
- `.env` file configured with DATABASE_URL and OPENAI_API_KEY

## Step 0: Start the Server

Open PowerShell in the project root and run:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to backend and start server
cd backend
python -m uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Leave this terminal running. Open a **NEW PowerShell window** for testing.

---

## Testing with Browser

### Test 1: Health Check
Open your browser and navigate to:
```
http://127.0.0.1:8000/api/v1/health
```

**Expected response:**
```json
{"status":"ok"}
```

### Test 2: API Documentation
FastAPI auto-generates interactive API documentation:
```
http://127.0.0.1:8000/docs
```

You can test all endpoints directly from this interface!

---

## Testing with PowerShell (New Window)

### Test 1: Health Check
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method GET
```

**Expected output:**
```
status
------
ok
```

### Test 2: Create a Job
```powershell
$jobData = @{
    title = "Backend Engineer"
    description = "Python, FastAPI, SQLAlchemy, PostgreSQL"
} | ConvertTo-Json

$job = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/jobs" -Method POST -Body $jobData -ContentType "application/json"
$job
```

**Save the job ID** from the response for later tests.

### Test 3: List All Jobs
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/jobs" -Method GET
```

### Test 4: Upload a Candidate Resume

**Note:** Update the file path to your actual resume location.

```powershell
# For PDF resume
curl.exe -X POST "http://127.0.0.1:8000/api/v1/candidates/upload" `
  -F "name=Supril Patil" `
  -F "email=supril@example.com" `
  -F "phone=9123456789" `
  -F "file=@C:\Users\supri\Desktop\resume.pdf"
```

**Expected response:**
```json
{
  "status": "uploaded",
  "candidate_id": 1
}
```

**Save the candidate ID** for later tests.

**Check server logs** - you should see background processing messages.

### Test 5: Wait and Get Candidate Details

Wait 3-5 seconds for background processing, then:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/candidates/1" -Method GET
```

**Expected:** You should see `resume_text` and `parsed_json` populated.

### Test 6: List All Candidates
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/candidates" -Method GET
```

### Test 7: Rank a Candidate for a Job

**Requirements:**
- OPENAI_API_KEY must be set in `.env`
- You need both a job_id and candidate_id from previous tests

```powershell
# Replace 1 with your actual job_id and candidate_id
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/jobs/1/rank/1" -Method POST
```

**Expected response:**
```json
{
  "candidate_id": 1,
  "job_id": 1,
  "score": 72.0,
  "details": {
    "score": 72,
    "top_matches": ["Python", "FastAPI", "SQLAlchemy"],
    "concerns": ["Limited cloud experience"],
    "reason": "Strong backend skills but needs cloud expertise"
  }
}
```

---

## Using the Python Test Script

I've created `test_api.py` for automated testing. To use it:

1. **Make sure the server is running** in another terminal
2. Open a **NEW PowerShell window**
3. Navigate to project root and activate venv:

```powershell
cd C:\Users\supri\ai-recruit-assistant
.\venv\Scripts\Activate.ps1
python test_api.py
```

**Note:** Update the resume path in `test_api.py` line 63 if needed.

---

## Troubleshooting

### 1. Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Fix:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env` has correct credentials
- Test connection: `psql -U postgres -d ai_recruit`

### 2. OpenAI Authentication Error
```
"could not get AI ranking", "reason": "error: 401"
```

**Fix:**
- Verify OPENAI_API_KEY in `.env` is correct and active
- Restart the server after changing `.env`
- Check your OpenAI account has API credits

### 3. File Upload 422 Error
```
422 Unprocessable Entity
```

**Fix:**
- Ensure using `-F` for form fields in curl
- File path must be prefixed with `@`
- Check file exists at specified path

### 4. Resume Text Not Populated

**Check:**
1. Look in `backend/uploads/` folder - is the file there?
2. Check server logs for "Error processing resume:"
3. Verify file permissions
4. Try re-uploading

### 5. CORS Errors in Browser

**Fix:**
- Add your frontend URL to `FRONTEND_ORIGIN` in `.env`
- Restart server after changing `.env`
- For testing, use `http://127.0.0.1:8000/docs` instead

---

## Checking the Database Directly

Using `psql`:

```powershell
# Connect to database (password: Supril@1616)
psql -U postgres -d ai_recruit

# View candidates
SELECT id, name, email, score FROM candidates ORDER BY created_at DESC;

# View jobs
SELECT id, title, description FROM jobs ORDER BY created_at DESC;

# Exit psql
\q
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/jobs` | Create a job |
| GET | `/api/v1/jobs` | List all jobs |
| GET | `/api/v1/jobs/{job_id}` | Get specific job |
| POST | `/api/v1/candidates/upload` | Upload resume |
| GET | `/api/v1/candidates` | List all candidates |
| GET | `/api/v1/candidates/{candidate_id}` | Get specific candidate |
| POST | `/api/v1/jobs/{job_id}/rank/{candidate_id}` | Rank candidate for job |

---

## Next Steps

1. **Fix Issues Found:** Address any errors discovered during testing
2. **Test Error Cases:** Try invalid data, missing fields, etc.
3. **Monitor Logs:** Watch server terminal for any warnings/errors
4. **Performance:** Test with multiple candidates and jobs
5. **Frontend:** Connect your frontend at `http://localhost:5500`

---

## Files Created for Testing

- `test_api.py` - Python automated test script
- `test_api.ps1` - PowerShell test script (may have execution policy issues)
- `TESTING_GUIDE.md` - This file

Happy Testing! 🚀
