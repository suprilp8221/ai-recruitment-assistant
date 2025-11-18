# API Testing Script for AI Recruitment Assistant
# Make sure the server is running before executing this script

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "API TESTING SCRIPT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000/api/v1"

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✓ Health check passed:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Create a Job
Write-Host "`nTest 2: Create a Job" -ForegroundColor Yellow
try {
    $jobData = @{
        title = "Backend Engineer"
        description = "Python, FastAPI, SQLAlchemy"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/jobs" -Method POST -Body $jobData -ContentType "application/json"
    Write-Host "✓ Job created:" -ForegroundColor Green
    $response | ConvertTo-Json
    $jobId = $response.id
} catch {
    Write-Host "✗ Job creation failed: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: List Jobs
Write-Host "`nTest 3: List Jobs" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/jobs" -Method GET
    Write-Host "✓ Jobs retrieved:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ List jobs failed: $_" -ForegroundColor Red
}

# Test 4: Upload a Candidate (if resume file exists)
Write-Host "`nTest 4: Upload a Candidate" -ForegroundColor Yellow
$resumePath = "C:\Users\supri\Desktop\resume.pdf"
if (Test-Path $resumePath) {
    try {
        # PowerShell multipart form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileBin = [System.IO.File]::ReadAllBytes($resumePath)
        $fileName = [System.IO.Path]::GetFileName($resumePath)
        
        # Build multipart body
        $bodyLines = @()
        $bodyLines += "--$boundary"
        $bodyLines += 'Content-Disposition: form-data; name="name"'
        $bodyLines += ''
        $bodyLines += 'Supril Patil'
        
        $bodyLines += "--$boundary"
        $bodyLines += 'Content-Disposition: form-data; name="email"'
        $bodyLines += ''
        $bodyLines += 'supril@example.com'
        
        $bodyLines += "--$boundary"
        $bodyLines += 'Content-Disposition: form-data; name="phone"'
        $bodyLines += ''
        $bodyLines += '9123456789'
        
        $bodyLines += "--$boundary"
        $bodyLines += "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`""
        $bodyLines += 'Content-Type: application/pdf'
        $bodyLines += ''
        
        $bodyString = [System.Text.Encoding]::UTF8.GetBytes(($bodyLines -join "`r`n") + "`r`n")
        $bodyEnd = [System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--`r`n")
        
        $requestBody = $bodyString + $fileBin + $bodyEnd
        
        $response = Invoke-RestMethod -Uri "$baseUrl/candidates/upload" -Method POST -Body $requestBody -ContentType "multipart/form-data; boundary=$boundary"
        Write-Host "✓ Candidate uploaded:" -ForegroundColor Green
        $response | ConvertTo-Json
        $candidateId = $response.candidate_id
        
        # Wait for background processing
        Write-Host "Waiting 3 seconds for background processing..." -ForegroundColor Cyan
        Start-Sleep -Seconds 3
        
        # Get candidate details
        Write-Host "`nTest 4b: Get Candidate Details" -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "$baseUrl/candidates/$candidateId" -Method GET
        Write-Host "✓ Candidate details:" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ Candidate upload failed: $_" -ForegroundColor Red
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "⚠ Resume file not found at: $resumePath" -ForegroundColor Yellow
    Write-Host "Skipping candidate upload test." -ForegroundColor Yellow
}

# Test 5: List Candidates
Write-Host "`nTest 5: List Candidates" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/candidates" -Method GET
    Write-Host "✓ Candidates retrieved:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ List candidates failed: $_" -ForegroundColor Red
}

# Test 6: Rank a Candidate (if we have both job and candidate)
if ($jobId -and $candidateId) {
    Write-Host "`nTest 6: Rank Candidate for Job" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/jobs/$jobId/rank/$candidateId" -Method POST
        Write-Host "✓ Ranking completed:" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ Ranking failed: $_" -ForegroundColor Red
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
