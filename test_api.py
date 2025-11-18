"""
API Testing Script for AI Recruitment Assistant
Run this while the server is running in another terminal
"""
import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_section(title):
    print(f"\n{'='*50}")
    print(f"{title}")
    print('='*50)

def test_health():
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_job():
    print_section("Test 2: Create a Job")
    try:
        data = {
            "title": "Backend Engineer",
            "description": "Python, FastAPI, SQLAlchemy"
        }
        response = requests.post(f"{BASE_URL}/jobs", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result.get('id') if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_list_jobs():
    print_section("Test 3: List Jobs")
    try:
        response = requests.get(f"{BASE_URL}/jobs")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload_candidate():
    print_section("Test 4: Upload a Candidate")
    resume_path = r"C:\Users\supri\Desktop\resume.pdf"
    
    if not os.path.exists(resume_path):
        print(f"⚠️  Resume file not found at: {resume_path}")
        print("Skipping upload test")
        return None
    
    try:
        files = {'file': open(resume_path, 'rb')}
        data = {
            'name': 'Supril Patil',
            'email': 'supril@example.com',
            'phone': '9123456789'
        }
        response = requests.post(f"{BASE_URL}/candidates/upload", files=files, data=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            candidate_id = result.get('candidate_id')
            print(f"\n⏳ Waiting 3 seconds for background processing...")
            time.sleep(3)
            
            # Get candidate details
            print_section("Test 4b: Get Candidate Details")
            response2 = requests.get(f"{BASE_URL}/candidates/{candidate_id}")
            print(f"Status: {response2.status_code}")
            result2 = response2.json()
            print(f"Response: {json.dumps(result2, indent=2)}")
            return candidate_id
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_list_candidates():
    print_section("Test 5: List Candidates")
    try:
        response = requests.get(f"{BASE_URL}/candidates")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rank_candidate(job_id, candidate_id):
    print_section("Test 6: Rank Candidate for Job")
    if not job_id or not candidate_id:
        print("⚠️  Skipping: job_id or candidate_id not available")
        return False
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/{job_id}/rank/{candidate_id}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("API TESTING SCRIPT")
    print("="*50)
    print("Make sure the server is running at http://127.0.0.1:8000")
    
    # Run tests
    test_health()
    job_id = test_create_job()
    test_list_jobs()
    candidate_id = test_upload_candidate()
    test_list_candidates()
    test_rank_candidate(job_id, candidate_id)
    
    print_section("TESTING COMPLETE")

if __name__ == "__main__":
    main()
