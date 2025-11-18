// API Base URL
const API_BASE = 'http://127.0.0.1:8000/api/v1';

// Global State
let candidates = [];
let jobs = [];
let interviews = [];
let currentSection = 'dashboard';
let currentInterviewFilter = 'all';

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    loadCandidates();
    loadJobs();
    loadInterviews();
    
    // Set up file input listener
    document.getElementById('resume-file').addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name;
        if (fileName) {
            document.getElementById('file-name').textContent = fileName;
        }
    });
});

// Navigation
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.add('hidden');
    });
    
    // Show selected section
    const sectionElement = document.getElementById(`${section}-section`);
    if (!sectionElement) {
        document.getElementById('dashboard-section').classList.remove('hidden');
        section = 'dashboard';
    } else {
        sectionElement.classList.remove('hidden');
    }
    
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event?.target?.classList.add('active');
    
    currentSection = section;
    
    // Load data for section
    if (section === 'candidates') loadCandidates();
    if (section === 'jobs') loadJobs();
    if (section === 'interviews') loadInterviews();
    if (section === 'ranking') loadRankingData();
}

// Dashboard Stats
async function loadDashboardStats() {
    try {
        const [candidatesRes, jobsRes, interviewsRes] = await Promise.all([
            fetch(`${API_BASE}/candidates/`),
            fetch(`${API_BASE}/jobs/`),
            fetch(`${API_BASE}/interviews/`)
        ]);
        
        const candidatesData = await candidatesRes.json();
        const jobsData = await jobsRes.json();
        const interviewsData = await interviewsRes.json();
        
        document.getElementById('stat-candidates').textContent = candidatesData.length;
        document.getElementById('stat-jobs').textContent = jobsData.length;
        document.getElementById('stat-interviews').textContent = interviewsData.length;
        
        // Calculate average score if available
        if (candidatesData.length > 0) {
            const avgScore = '-';
            document.getElementById('stat-avg-score').textContent = avgScore;
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Candidates Functions
async function loadCandidates() {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/candidates/`);
        candidates = await response.json();
        renderCandidates(candidates);
    } catch (error) {
        showToast('Error', 'Failed to load candidates', 'error');
        console.error('Error loading candidates:', error);
    } finally {
        showLoading(false);
    }
}

function renderCandidates(candidatesList) {
    const container = document.getElementById('candidates-list');
    
    if (candidatesList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-users"></i>
                <h3>No candidates yet</h3>
                <p>Upload a resume to get started</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = candidatesList.map(candidate => `
        <div class="candidate-card">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h3 class="text-xl font-bold text-gray-800 mb-2">
                        <i class="fas fa-user mr-2 text-blue-600"></i>${candidate.name}
                    </h3>
                    <div class="space-y-1 text-gray-600">
                        ${candidate.email ? `<p><i class="fas fa-envelope mr-2"></i>${candidate.email}</p>` : ''}
                        ${candidate.phone ? `<p><i class="fas fa-phone mr-2"></i>${candidate.phone}</i></p>` : ''}
                        ${candidate.parsed_data?.skills ? `
                            <div class="mt-2">
                                <p class="font-medium text-gray-700 mb-1">Skills:</p>
                                <div class="flex flex-wrap gap-2">
                                    ${candidate.parsed_data.skills.slice(0, 5).map(skill => 
                                        `<span class="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">${skill}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="ml-4">
                    <button onclick="viewCandidate(${candidate.id})" class="text-blue-600 hover:text-blue-700 px-3 py-1 border border-blue-600 rounded hover:bg-blue-50">
                        <i class="fas fa-eye mr-1"></i>View
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function searchCandidates() {
    const searchTerm = document.getElementById('candidate-search').value.toLowerCase();
    const filtered = candidates.filter(c => 
        c.name.toLowerCase().includes(searchTerm) ||
        (c.email && c.email.toLowerCase().includes(searchTerm))
    );
    renderCandidates(filtered);
}

async function viewCandidate(id) {
    const candidate = candidates.find(c => c.id === id);
    if (candidate) {
        alert(`Candidate Details:\n\nName: ${candidate.name}\nEmail: ${candidate.email || 'N/A'}\nPhone: ${candidate.phone || 'N/A'}\n\nParsed Data:\n${JSON.stringify(candidate.parsed_data, null, 2)}`);
    }
}

// Upload Modal Functions
function showUploadModal() {
    document.getElementById('upload-modal').classList.remove('hidden');
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    document.getElementById('upload-form').reset();
    document.getElementById('file-name').textContent = '';
}

async function uploadResume(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('candidate-name').value);
    formData.append('email', document.getElementById('candidate-email').value);
    formData.append('phone', document.getElementById('candidate-phone').value);
    formData.append('file', document.getElementById('resume-file').files[0]);
    
    try {
        showLoading(true);
        console.log('Uploading resume...', {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            file: formData.get('file')?.name
        });
        
        const response = await fetch(`${API_BASE}/candidates/upload`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Upload response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Upload successful:', result);
            showToast('Success', 'Resume uploaded and parsed successfully!', 'success');
            closeUploadModal();
            loadCandidates();
            loadDashboardStats();
        } else {
            const error = await response.json();
            console.error('Upload failed:', error);
            showToast('Error', error.detail || 'Failed to upload resume', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast('Error', `Failed to upload resume: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Drag and Drop Handlers
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        document.getElementById('resume-file').files = event.dataTransfer.files;
        document.getElementById('file-name').textContent = file.name;
    }
}

// Jobs Functions
async function loadJobs() {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/jobs/`);
        jobs = await response.json();
        renderJobs(jobs);
    } catch (error) {
        showToast('Error', 'Failed to load jobs', 'error');
        console.error('Error loading jobs:', error);
    } finally {
        showLoading(false);
    }
}

function renderJobs(jobsList) {
    const container = document.getElementById('jobs-list');
    
    if (jobsList.length === 0) {
        container.innerHTML = `
            <div class="empty-state col-span-2">
                <i class="fas fa-briefcase"></i>
                <h3>No job postings yet</h3>
                <p>Create your first job posting</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = jobsList.map(job => `
        <div class="job-card">
            <h3 class="text-xl font-bold text-gray-800 mb-3">
                <i class="fas fa-briefcase mr-2 text-green-600"></i>${job.title}
            </h3>
            <p class="text-gray-600 mb-4 line-clamp-3">${job.description}</p>
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500">
                    <i class="fas fa-calendar mr-1"></i>
                    Posted ${new Date(job.created_at).toLocaleDateString()}
                </span>
                <div class="space-x-2">
                    <button onclick="viewJob(${job.id})" class="text-green-600 hover:text-green-700 px-3 py-1 border border-green-600 rounded hover:bg-green-50">
                        <i class="fas fa-eye mr-1"></i>View
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewJob(id) {
    const job = jobs.find(j => j.id === id);
    if (job) {
        alert(`Job Details:\n\nTitle: ${job.title}\n\nDescription:\n${job.description}`);
    }
}

// Job Modal Functions
function showJobModal() {
    document.getElementById('job-modal').classList.remove('hidden');
}

function closeJobModal() {
    document.getElementById('job-modal').classList.add('hidden');
    document.getElementById('job-form').reset();
}

async function createJob(event) {
    event.preventDefault();
    
    const jobData = {
        title: document.getElementById('job-title').value,
        description: document.getElementById('job-description').value
    };
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/jobs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        if (response.ok) {
            showToast('Success', 'Job posting created successfully!', 'success');
            closeJobModal();
            loadJobs();
            loadDashboardStats();
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to create job', 'error');
        }
    } catch (error) {
        showToast('Error', 'Failed to create job', 'error');
        console.error('Create job error:', error);
    } finally {
        showLoading(false);
    }
}

// Interviews Functions
async function loadInterviews() {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/interviews/`);
        interviews = await response.json();
        renderInterviews(interviews);
    } catch (error) {
        showToast('Error', 'Failed to load interviews', 'error');
        console.error('Error loading interviews:', error);
    } finally {
        showLoading(false);
    }
}

function renderInterviews(interviewsList) {
    const container = document.getElementById('interviews-list');
    
    if (interviewsList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-alt"></i>
                <h3>No interviews scheduled</h3>
                <p>Schedule your first interview</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = interviewsList.map(interview => {
        const scheduledDate = new Date(interview.scheduled_time);
        const candidate = candidates.find(c => c.id === interview.candidate_id);
        const job = jobs.find(j => j.id === interview.job_id);
        
        return `
            <div class="interview-card">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center mb-2">
                            <h3 class="text-lg font-bold text-gray-800">
                                ${candidate?.name || `Candidate #${interview.candidate_id}`}
                            </h3>
                            <span class="status-badge status-scheduled ml-3">Scheduled</span>
                        </div>
                        <div class="space-y-1 text-gray-600">
                            ${job ? `<p><i class="fas fa-briefcase mr-2"></i>${job.title}</p>` : ''}
                            <p><i class="fas fa-calendar mr-2"></i>${scheduledDate.toLocaleDateString()} at ${scheduledDate.toLocaleTimeString()}</p>
                            ${interview.interviewer ? `<p><i class="fas fa-user-tie mr-2"></i>${interview.interviewer}</p>` : ''}
                            ${interview.notes ? `<p class="mt-2 text-sm"><i class="fas fa-sticky-note mr-2"></i>${interview.notes}</p>` : ''}
                        </div>
                    </div>
                    <div class="ml-4">
                        <button onclick="editInterview(${interview.id})" class="text-purple-600 hover:text-purple-700 px-3 py-1 border border-purple-600 rounded hover:bg-purple-50">
                            <i class="fas fa-edit mr-1"></i>Edit
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterInterviews(filter) {
    currentInterviewFilter = filter;
    
    // Update button styles
    document.querySelectorAll('.interview-filter-btn').forEach(btn => {
        btn.classList.remove('active', 'bg-purple-100', 'text-purple-700');
        btn.classList.add('text-gray-600', 'hover:bg-gray-100');
    });
    event.target.classList.remove('text-gray-600', 'hover:bg-gray-100');
    event.target.classList.add('active', 'bg-purple-100', 'text-purple-700');
    
    // Filter interviews
    let filtered = interviews;
    if (filter === 'upcoming') {
        const now = new Date();
        filtered = interviews.filter(i => new Date(i.scheduled_time) > now);
    }
    
    renderInterviews(filtered);
}

async function editInterview(id) {
    const interview = interviews.find(i => i.id === id);
    if (interview) {
        alert(`Interview edit functionality would be implemented here.\n\nInterview ID: ${id}`);
    }
}

// Interview Modal Functions
function showInterviewModal() {
    document.getElementById('interview-modal').classList.remove('hidden');
    
    // Populate candidate dropdown
    const candidateSelect = document.getElementById('interview-candidate');
    candidateSelect.innerHTML = '<option value="">Select candidate...</option>' +
        candidates.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    
    // Populate job dropdown
    const jobSelect = document.getElementById('interview-job');
    jobSelect.innerHTML = '<option value="">Select job (optional)...</option>' +
        jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
}

function closeInterviewModal() {
    document.getElementById('interview-modal').classList.add('hidden');
    document.getElementById('interview-form').reset();
}

async function scheduleInterview(event) {
    event.preventDefault();
    
    const interviewData = {
        candidate_id: parseInt(document.getElementById('interview-candidate').value),
        job_id: document.getElementById('interview-job').value ? parseInt(document.getElementById('interview-job').value) : null,
        scheduled_time: new Date(document.getElementById('interview-datetime').value).toISOString(),
        interviewer: document.getElementById('interview-interviewer').value || null,
        notes: document.getElementById('interview-notes').value || null
    };
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/interviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(interviewData)
        });
        
        if (response.ok) {
            showToast('Success', 'Interview scheduled successfully!', 'success');
            closeInterviewModal();
            loadInterviews();
            loadDashboardStats();
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to schedule interview', 'error');
        }
    } catch (error) {
        showToast('Error', 'Failed to schedule interview', 'error');
        console.error('Schedule interview error:', error);
    } finally {
        showLoading(false);
    }
}

// Ranking Functions
async function loadRankingData() {
    // Populate job dropdown
    const jobSelect = document.getElementById('rank-job-select');
    jobSelect.innerHTML = '<option value="">Choose a job...</option>' +
        jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
    
    // Populate candidate dropdown
    const candidateSelect = document.getElementById('rank-candidate-select');
    candidateSelect.innerHTML = '<option value="">Choose a candidate...</option>' +
        candidates.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

async function rankCandidate() {
    const jobId = document.getElementById('rank-job-select').value;
    const candidateId = document.getElementById('rank-candidate-select').value;
    
    if (!jobId || !candidateId) {
        showToast('Error', 'Please select both a job and a candidate', 'error');
        return;
    }
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/jobs/${jobId}/rank/${candidateId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            displayRankingResult(result);
            showToast('Success', 'Candidate ranked successfully!', 'success');
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to rank candidate', 'error');
        }
    } catch (error) {
        showToast('Error', 'Failed to rank candidate', 'error');
        console.error('Ranking error:', error);
    } finally {
        showLoading(false);
    }
}

function displayRankingResult(result) {
    const resultContainer = document.getElementById('ranking-result');
    const job = jobs.find(j => j.id === result.job_id);
    const candidate = candidates.find(c => c.id === result.candidate_id);
    
    let scoreClass = 'score-low';
    if (result.score >= 70) scoreClass = 'score-high';
    else if (result.score >= 50) scoreClass = 'score-medium';
    
    resultContainer.innerHTML = `
        <div class="text-center mb-6">
            <h3 class="text-2xl font-bold text-gray-800 mb-2">Ranking Result</h3>
            <p class="text-gray-600">${candidate?.name} for ${job?.title}</p>
        </div>
        <div class="text-center mb-6">
            <div class="inline-block">
                <div class="text-6xl font-bold mb-2">
                    <span class="score-badge ${scoreClass}" style="font-size: 3rem; padding: 1rem 2rem;">
                        ${result.score}/100
                    </span>
                </div>
                <p class="text-gray-600">Match Score</p>
            </div>
        </div>
        ${result.details ? `
            <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-bold text-gray-800 mb-2">Details:</h4>
                <p class="text-gray-700 whitespace-pre-wrap">${result.details}</p>
            </div>
        ` : ''}
    `;
    
    resultContainer.classList.remove('hidden');
}

// Utility Functions
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toast-icon');
    const titleElement = document.getElementById('toast-title');
    const messageElement = document.getElementById('toast-message');
    
    // Set icon and colors based on type
    if (type === 'success') {
        icon.className = 'fas fa-check-circle text-green-600 text-2xl mr-3';
    } else if (type === 'error') {
        icon.className = 'fas fa-times-circle text-red-600 text-2xl mr-3';
    } else {
        icon.className = 'fas fa-info-circle text-blue-600 text-2xl mr-3';
    }
    
    titleElement.textContent = title;
    messageElement.textContent = message;
    
    // Show toast
    toast.classList.remove('hidden');
    toast.classList.add('toast-show');
    
    // Hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.classList.remove('toast-hide');
        }, 400);
    }, 4000);
}
