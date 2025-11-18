# 🤖 AI Recruitment Assistant

An AI-powered recruitment platform that streamlines the hiring process with intelligent resume parsing, candidate ranking, and interview management.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)](https://openai.com/)

## ✨ Features

### ✅ Phase 1: Core Backend (COMPLETE)

#### 🧠 AI Resume Parsing
- **Intelligent Text Extraction**: Automatically extract text from PDF and DOCX resumes
- **Structured Data Parsing**: AI-powered extraction of contact info, skills, experience, education, certifications, languages, and projects
- **Fallback Mechanism**: Graceful degradation from AI to basic parsing if needed
- **JSON Schema Validation**: Normalized, consistent data structure

#### 📅 Interview Management
- **Complete CRUD Operations**: Create, read, update, delete interviews
- **Candidate-to-Job Linking**: Associate interviews with specific job openings
- **Scheduling**: Track interview dates, times, and interviewers
- **Notes System**: Add feedback and notes after interviews
- **Advanced Filtering**: Filter by candidate, job, or upcoming interviews

#### 🛡️ Error Handling & Logging
- **Custom Exceptions**: 9 specialized exception classes for different error scenarios
- **Structured Logging**: Color-coded console output with daily log file rotation
- **Comprehensive Error Tracking**: All operations logged with timestamps and context
- **Global Exception Handlers**: Graceful error responses for all API endpoints

#### 🔒 Input Validation & Security
- **File Upload Security**: Type validation, size limits (10MB), filename sanitization
- **Pydantic Validators**: Field-level validation on all input models
- **Data Constraints**: String length limits, format validation (email, phone)
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── candidates.py   # Resume upload, listing
│   │   ├── jobs.py         # Job postings CRUD
│   │   ├── interviews.py   # Interview management
│   │   └── ranking.py      # AI candidate ranking
│   │
│   ├── core/            # Core utilities
│   │   ├── exceptions.py   # Custom exceptions
│   │   ├── logging_config.py  # Logging setup
│   │   └── security.py     # Validation & security
│   │
│   ├── db/              # Database layer
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── crud.py         # Database operations
│   │   └── database.py     # DB connection
│   │
│   ├── services/        # Business logic
│   │   ├── ai_resume_parser.py  # OpenAI parsing
│   │   ├── resume_parser.py     # Text extraction
│   │   └── ranking.py           # AI ranking
│   │
│   └── schemas/         # Pydantic models
│       └── schemas.py      # Request/response schemas
│
└── frontend/            # (Phase 2 - Planned)
    ├── index.html
    ├── styles.css
    └── app.js
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/suprilp8221/ai-recruitment-assistant.git
cd ai-recruitment-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL: PostgreSQL connection string
# - OPENAI_API_KEY: Your OpenAI API key
```

5. **Create database**
```sql
CREATE DATABASE ai_recruit;
```

6. **Run the server**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

## 📚 API Documentation

### Candidates
- `POST /api/v1/candidates/upload` - Upload resume with candidate info
- `GET /api/v1/candidates` - List all candidates
- `GET /api/v1/candidates/{id}` - Get specific candidate

### Jobs
- `POST /api/v1/jobs` - Create job posting
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{id}` - Get specific job

### Interviews
- `POST /api/v1/interviews` - Schedule interview
- `GET /api/v1/interviews` - List interviews (filterable)
- `GET /api/v1/interviews/{id}` - Get interview details
- `PUT /api/v1/interviews/{id}` - Update interview
- `DELETE /api/v1/interviews/{id}` - Cancel interview
- `PUT /api/v1/interviews/{id}/notes` - Add interview notes

### Ranking
- `POST /api/v1/jobs/{job_id}/rank/{candidate_id}` - AI-rank candidate for job

## 🛠️ Tech Stack

**Backend:**
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Relational database with JSONB support
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Pydantic V2** - Data validation using Python type annotations
- **OpenAI GPT-3.5** - AI-powered resume parsing and ranking
- **pdfminer.six** - PDF text extraction
- **python-docx** - DOCX text extraction

**Development:**
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management

## 📋 Roadmap

- [x] **Phase 1: Core Backend** (COMPLETE)
  - [x] AI Resume Parsing
  - [x] Interview Management
  - [x] Error Handling & Logging
  - [x] Input Validation & Security

- [ ] **Phase 2: Frontend Development** (8-12 hours)
  - [ ] Responsive UI with Tailwind CSS
  - [ ] Candidate upload interface
  - [ ] Job posting management
  - [ ] Ranking visualization
  - [ ] Interview calendar

- [ ] **Phase 3: Advanced AI Features** (4-6 hours)
  - [ ] Interview question generation
  - [ ] Candidate matching algorithm
  - [ ] Resume quality scoring
  - [ ] Skill gap analysis

- [ ] **Phase 4: Authentication** (3-4 hours)
  - [ ] User registration/login
  - [ ] JWT token management
  - [ ] Role-based access control

- [ ] **Phase 5: Analytics & Reporting** (4-5 hours)
  - [ ] Dashboard with metrics
  - [ ] Export capabilities
  - [ ] Hiring pipeline visualization

## 🧪 Testing

Run the verification script:
```bash
cd backend
python test_phase1.py
```

Or use the API docs at `http://127.0.0.1:8000/docs` for interactive testing.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Supril Patel**
- GitHub: [@suprilp8221](https://github.com/suprilp8221)
- Repository: [ai-recruitment-assistant](https://github.com/suprilp8221/ai-recruitment-assistant)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show your support

Give a ⭐️ if this project helped you!

---

**Status**: ✅ Phase 1 Complete | 📅 Last Updated: November 18, 2025
Short: a simple app using FastAPI + PostgreSQL + OpenAI + LangChain for resume ranking and interview feedback.
Provide steps to run locally without Docker: create venv, install requirements, create DB, run server.
