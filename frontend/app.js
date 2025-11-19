// API Base URL
const API_BASE = 'http://127.0.0.1:8000/api/v1';

// Authentication State
let authToken = null;
let currentUser = null;

// Global State
let candidates = [];
let jobs = [];
let interviews = [];
let currentSection = 'dashboard';
let currentInterviewFilter = 'all';

// Check authentication on page load
function checkAuth() {
    authToken = localStorage.getItem('accessToken');
    const userData = localStorage.getItem('userData');
    
    if (!authToken || !userData) {
        // Redirect to login
        window.location.href = 'login.html';
        return false;
    }
    
    try {
        currentUser = JSON.parse(userData);
        updateUserUI();
        return true;
    } catch (error) {
        console.error('Error parsing user data:', error);
        logout();
        return false;
    }
}

// Update UI with user information
function updateUserUI() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.name;
        document.getElementById('user-email').textContent = currentUser.email;
        document.getElementById('user-role').textContent = `Role: ${capitalizeFirst(currentUser.role)}`;
    }
}

// Capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Logout function
function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userData');
    window.location.href = 'login.html';
}

// Toggle user menu
document.addEventListener('DOMContentLoaded', () => {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuButton.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
});

// Fetch with authentication
async function fetchWithAuth(url, options = {}) {
    if (!authToken) {
        logout();
        throw new Error('No authentication token');
    }
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`
    };
    
    // Add Content-Type for JSON requests
    if (options.body && typeof options.body === 'string') {
        headers['Content-Type'] = 'application/json';
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // Handle unauthorized responses
    if (response.status === 401) {
        showToast('Error', 'Session expired. Please login again.', 'error');
        logout();
        throw new Error('Unauthorized');
    }
    
    // Handle forbidden responses
    if (response.status === 403) {
        showToast('Error', 'You do not have permission to perform this action.', 'error');
        throw new Error('Forbidden');
    }
    
    return response;
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication first
    if (!checkAuth()) {
        return;
    }
    
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
            fetchWithAuth(`${API_BASE}/candidates/`),
            fetchWithAuth(`${API_BASE}/jobs/`),
            fetchWithAuth(`${API_BASE}/interviews/`)
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
        const response = await fetchWithAuth(`${API_BASE}/candidates/`);
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
                <div class="ml-4 flex flex-col gap-2">
                    <button onclick="viewCandidate(${candidate.id})" class="text-blue-600 hover:text-blue-700 px-3 py-1 border border-blue-600 rounded hover:bg-blue-50">
                        <i class="fas fa-eye mr-1"></i>View
                    </button>
                    <button onclick="showOptimizerModal(${candidate.id})" class="text-green-600 hover:text-green-700 px-3 py-1 border border-green-600 rounded hover:bg-green-50">
                        <i class="fas fa-file-alt mr-1"></i>Optimize
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
        
        const response = await fetchWithAuth(`${API_BASE}/candidates/upload`, {
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
        const response = await fetchWithAuth(`${API_BASE}/jobs/`);
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
        const response = await fetchWithAuth(`${API_BASE}/jobs/`, {
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
        const response = await fetchWithAuth(`${API_BASE}/interviews/`);
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
                    <div class="ml-4 space-x-2">
                        <button onclick="showFeedbackModal(${interview.id})" class="text-blue-600 hover:text-blue-700 px-3 py-1 border border-blue-600 rounded hover:bg-blue-50">
                            <i class="fas fa-chart-line mr-1"></i>Analyze
                        </button>
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
async function showInterviewModal() {
    document.getElementById('interview-modal').classList.remove('hidden');
    
    // Ensure data is loaded
    if (candidates.length === 0) await loadCandidates();
    if (jobs.length === 0) await loadJobs();
    
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
        const response = await fetchWithAuth(`${API_BASE}/interviews/`, {
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
    // Ensure data is loaded
    if (candidates.length === 0) await loadCandidates();
    if (jobs.length === 0) await loadJobs();
    
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
        const response = await fetchWithAuth(`${API_BASE}/jobs/${jobId}/rank/${candidateId}`, {
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
    } else if (type === 'warning') {
        icon.className = 'fas fa-exclamation-triangle text-yellow-600 text-2xl mr-3';
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

// Interview Questions Generator Functions
let generatedQuestions = null;

async function showQuestionsModal() {
    document.getElementById('questions-modal').classList.remove('hidden');
    
    // Ensure data is loaded
    if (candidates.length === 0) await loadCandidates();
    if (jobs.length === 0) await loadJobs();
    
    // Check if we have the required data
    if (jobs.length === 0) {
        showToast('Warning', 'Please create at least one job posting first', 'warning');
    }
    if (candidates.length === 0) {
        showToast('Warning', 'Please upload at least one candidate resume first', 'warning');
    }
    
    // Populate job dropdown
    const jobSelect = document.getElementById('questions-job-select');
    jobSelect.innerHTML = '<option value="">Choose a job...</option>' +
        jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
    
    // Populate candidate dropdown
    const candidateSelect = document.getElementById('questions-candidate-select');
    candidateSelect.innerHTML = '<option value="">Choose a candidate...</option>' +
        candidates.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    
    // Reset form
    resetQuestionsForm();
}

function closeQuestionsModal() {
    document.getElementById('questions-modal').classList.add('hidden');
    resetQuestionsForm();
}

function resetQuestionsForm() {
    document.getElementById('questions-form-section').classList.remove('hidden');
    document.getElementById('questions-result-section').classList.add('hidden');
    document.getElementById('questions-count').value = 10;
    document.getElementById('questions-difficulty').value = 'medium';
    generatedQuestions = null;
}

async function generateQuestions() {
    const jobId = document.getElementById('questions-job-select').value;
    const candidateId = document.getElementById('questions-candidate-select').value;
    const count = parseInt(document.getElementById('questions-count').value);
    const difficulty = document.getElementById('questions-difficulty').value;
    
    if (!jobId || !candidateId) {
        showToast('Error', 'Please select both a job and a candidate', 'error');
        return;
    }
    
    const requestData = {
        job_id: parseInt(jobId),
        candidate_id: parseInt(candidateId),
        count: count,
        difficulty: difficulty,
        question_types: ['technical', 'behavioral', 'situational']
    };
    
    try {
        showLoading(true);
        console.log('Generating interview questions...', requestData);
        
        const response = await fetchWithAuth(`${API_BASE}/ai/generate-questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Questions response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Questions generated:', result);
            generatedQuestions = result;
            displayGeneratedQuestions(result);
            showToast('Success', `Generated ${result.total_questions} interview questions!`, 'success');
        } else {
            const error = await response.json();
            console.error('Failed to generate questions:', error);
            showToast('Error', error.detail || 'Failed to generate questions', 'error');
        }
    } catch (error) {
        console.error('Generate questions error:', error);
        showToast('Error', `Failed to generate questions: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayGeneratedQuestions(result) {
    // Hide form, show results
    document.getElementById('questions-form-section').classList.add('hidden');
    document.getElementById('questions-result-section').classList.remove('hidden');
    
    // Set title
    const title = `${result.total_questions} Questions for ${result.candidate_name} - ${result.job_title}`;
    document.getElementById('questions-result-title').textContent = title;
    
    // Build questions HTML
    const container = document.getElementById('questions-content');
    
    // Group questions by category
    const categories = {
        'technical': { icon: 'fa-code', color: 'blue', title: 'Technical Questions' },
        'behavioral': { icon: 'fa-users', color: 'green', title: 'Behavioral Questions' },
        'situational': { icon: 'fa-lightbulb', color: 'orange', title: 'Situational Questions' },
        'culture_fit': { icon: 'fa-heart', color: 'pink', title: 'Culture Fit Questions' }
    };
    
    let html = '';
    
    // Add model info badge
    const modelBadge = result.model_used === 'gpt-3.5-turbo' 
        ? '<span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium"><i class="fas fa-robot mr-1"></i>AI Generated</span>'
        : '<span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium"><i class="fas fa-list mr-1"></i>Template</span>';
    
    html += `<div class="mb-4 flex justify-between items-center">
        <span class="text-sm text-gray-600">Experience Level: <strong class="capitalize">${result.experience_level}</strong></span>
        ${modelBadge}
    </div>`;
    
    // Display questions by category
    for (const [categoryKey, categoryInfo] of Object.entries(categories)) {
        const categoryQuestions = result.categorized[categoryKey] || [];
        
        if (categoryQuestions.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="text-lg font-bold text-gray-800 mb-3 flex items-center">
                        <i class="fas ${categoryInfo.icon} text-${categoryInfo.color}-600 mr-2"></i>
                        ${categoryInfo.title} (${categoryQuestions.length})
                    </h4>
                    <div class="space-y-3">
            `;
            
            categoryQuestions.forEach((q, index) => {
                const difficultyColors = {
                    'easy': 'green',
                    'medium': 'yellow',
                    'hard': 'red'
                };
                const diffColor = difficultyColors[q.difficulty] || 'gray';
                
                html += `
                    <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                        <div class="flex items-start justify-between mb-2">
                            <span class="font-medium text-gray-800">Q${index + 1}.</span>
                            <div class="flex gap-2">
                                <span class="bg-${diffColor}-100 text-${diffColor}-700 px-2 py-1 rounded text-xs font-medium capitalize">
                                    ${q.difficulty}
                                </span>
                                ${q.category ? `<span class="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">${q.category}</span>` : ''}
                            </div>
                        </div>
                        <p class="text-gray-700 ml-6">${q.question}</p>
                        ${q.follow_up ? `<p class="text-gray-500 text-sm ml-6 mt-2 italic"><i class="fas fa-arrow-right mr-1"></i>Follow-up: ${q.follow_up}</p>` : ''}
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    container.innerHTML = html;
}

function copyQuestionsToClipboard() {
    if (!generatedQuestions) return;
    
    let text = `Interview Questions for ${generatedQuestions.candidate_name} - ${generatedQuestions.job_title}\n`;
    text += `Experience Level: ${generatedQuestions.experience_level}\n`;
    text += `Total Questions: ${generatedQuestions.total_questions}\n`;
    text += `Generated by: ${generatedQuestions.model_used}\n\n`;
    
    generatedQuestions.questions.forEach((q, index) => {
        text += `${index + 1}. [${q.type.toUpperCase()}] [${q.difficulty.toUpperCase()}] ${q.category || ''}\n`;
        text += `   ${q.question}\n`;
        if (q.follow_up) {
            text += `   Follow-up: ${q.follow_up}\n`;
        }
        text += `\n`;
    });
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Success', 'Questions copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('Error', 'Failed to copy to clipboard', 'error');
    });
}

// ============================================================================
// Interview Feedback Analysis Functions
// ============================================================================

let currentInterviewForFeedback = null;
let currentFeedbackAnalysis = null;

function showFeedbackModal(interviewId) {
    const interview = interviews.find(i => i.id === interviewId);
    if (!interview) {
        showToast('Error', 'Interview not found', 'error');
        return;
    }
    
    currentInterviewForFeedback = interview;
    
    // Get candidate and job details
    const candidate = candidates.find(c => c.id === interview.candidate_id);
    const job = jobs.find(j => j.id === interview.job_id);
    
    // Set modal title
    const title = `${candidate?.name || 'Candidate'} - ${job?.title || 'Interview'}`;
    document.getElementById('feedback-interview-title').textContent = title;
    
    // Pre-fill notes if they exist
    document.getElementById('feedback-notes').value = interview.notes || '';
    
    // Show modal
    document.getElementById('feedback-modal').classList.remove('hidden');
    resetFeedbackForm();
}

function closeFeedbackModal() {
    document.getElementById('feedback-modal').classList.add('hidden');
    currentInterviewForFeedback = null;
    currentFeedbackAnalysis = null;
}

function resetFeedbackForm() {
    document.getElementById('feedback-input-section').classList.remove('hidden');
    document.getElementById('feedback-results-section').classList.add('hidden');
    currentFeedbackAnalysis = null;
}

async function analyzeFeedback() {
    const notes = document.getElementById('feedback-notes').value.trim();
    
    if (!notes || notes.length < 10) {
        showToast('Error', 'Please enter at least 10 characters of interview feedback', 'error');
        return;
    }
    
    if (!currentInterviewForFeedback) {
        showToast('Error', 'No interview selected', 'error');
        return;
    }
    
    try {
        showLoading(true);
        console.log('Analyzing feedback for interview:', currentInterviewForFeedback.id);
        
        const response = await fetchWithAuth(`${API_BASE}/ai/interviews/${currentInterviewForFeedback.id}/analyze-feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                interview_notes: notes
            })
        });
        
        if (response.ok) {
            const analysis = await response.json();
            currentFeedbackAnalysis = analysis;
            displayFeedbackAnalysis(analysis);
            showToast('Success', 'Feedback analyzed successfully!', 'success');
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to analyze feedback', 'error');
        }
    } catch (error) {
        showToast('Error', 'Failed to analyze feedback', 'error');
        console.error('Analysis error:', error);
    } finally {
        showLoading(false);
    }
}

function displayFeedbackAnalysis(analysis) {
    // Hide input section, show results
    document.getElementById('feedback-input-section').classList.add('hidden');
    document.getElementById('feedback-results-section').classList.remove('hidden');
    
    // Set recommendation badge
    const badge = document.getElementById('feedback-recommendation-badge');
    const recommendation = analysis.recommendation.toLowerCase();
    
    if (recommendation === 'hire') {
        badge.className = 'px-4 py-2 rounded-lg font-bold text-white bg-green-600';
        badge.innerHTML = '<i class="fas fa-thumbs-up mr-2"></i>HIRE';
    } else if (recommendation === 'no-hire') {
        badge.className = 'px-4 py-2 rounded-lg font-bold text-white bg-red-600';
        badge.innerHTML = '<i class="fas fa-thumbs-down mr-2"></i>NO HIRE';
    } else {
        badge.className = 'px-4 py-2 rounded-lg font-bold text-white bg-yellow-600';
        badge.innerHTML = '<i class="fas fa-question mr-2"></i>MAYBE';
    }
    
    // Set confidence score
    const confidence = analysis.confidence_score;
    document.getElementById('feedback-confidence-value').textContent = `${confidence}%`;
    document.getElementById('feedback-confidence-bar').style.width = `${confidence}%`;
    
    // Set confidence bar color based on level
    const confidenceBar = document.getElementById('feedback-confidence-bar');
    if (confidence >= 80) {
        confidenceBar.className = 'bg-green-600 h-3 rounded-full transition-all';
    } else if (confidence >= 60) {
        confidenceBar.className = 'bg-yellow-600 h-3 rounded-full transition-all';
    } else {
        confidenceBar.className = 'bg-red-600 h-3 rounded-full transition-all';
    }
    
    // Set skills ratings
    document.getElementById('feedback-technical-rating').textContent = 
        analysis.technical_skills_rating ? `${analysis.technical_skills_rating}/5` : '-';
    document.getElementById('feedback-communication-rating').textContent = 
        analysis.communication_skills_rating ? `${analysis.communication_skills_rating}/5` : '-';
    document.getElementById('feedback-culture-rating').textContent = 
        analysis.culture_fit_rating ? `${analysis.culture_fit_rating}/5` : '-';
    
    // Set strengths
    const strengthsList = document.getElementById('feedback-strengths-list');
    strengthsList.innerHTML = analysis.strengths.map(s => 
        `<li class="flex items-start">
            <i class="fas fa-plus-circle text-green-600 mt-1 mr-2"></i>
            <span class="text-gray-700">${s}</span>
        </li>`
    ).join('');
    
    // Set weaknesses
    const weaknessesList = document.getElementById('feedback-weaknesses-list');
    weaknessesList.innerHTML = analysis.weaknesses.map(w => 
        `<li class="flex items-start">
            <i class="fas fa-minus-circle text-orange-600 mt-1 mr-2"></i>
            <span class="text-gray-700">${w}</span>
        </li>`
    ).join('');
    
    // Set overall assessment
    document.getElementById('feedback-overall-assessment').textContent = analysis.overall_assessment;
    
    // Set reasoning
    document.getElementById('feedback-reasoning').textContent = analysis.reasoning;
    
    // Set next steps
    const nextStepsList = document.getElementById('feedback-next-steps-list');
    nextStepsList.innerHTML = analysis.next_steps.map(step => 
        `<li class="text-gray-700">${step}</li>`
    ).join('');
}


// ============================================
// Resume Optimizer Functions
// ============================================

let currentCandidateId = null;

function showOptimizerModal(candidateId) {
    currentCandidateId = candidateId;
    const modal = document.getElementById('optimizer-modal');
    modal.classList.remove('hidden');
    
    // Show loading state
    document.getElementById('optimizer-loading').classList.remove('hidden');
    document.getElementById('optimizer-results').classList.add('hidden');
    
    // Trigger analysis
    analyzeResume(candidateId);
}

function closeOptimizerModal() {
    const modal = document.getElementById('optimizer-modal');
    modal.classList.add('hidden');
    currentCandidateId = null;
}

async function analyzeResume(candidateId) {
    try {
        const response = await fetchWithAuth(`${API_BASE}/ai/candidates/${candidateId}/optimize-resume`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to analyze resume');
        }
        
        const analysis = await response.json();
        displayOptimizationResults(analysis);
        
    } catch (error) {
        console.error('Error analyzing resume:', error);
        showToast('Failed to analyze resume: ' + error.message, 'error');
        closeOptimizerModal();
    }
}

function displayOptimizationResults(analysis) {
    // Hide loading, show results
    document.getElementById('optimizer-loading').classList.add('hidden');
    document.getElementById('optimizer-results').classList.remove('hidden');
    
    // Set ATS Score with animation
    const score = analysis.ats_score;
    const scoreValue = document.getElementById('ats-score-value');
    const scoreCircle = document.getElementById('ats-score-circle');
    const scoreLabel = document.getElementById('ats-score-label');
    
    // Animate score
    let currentScore = 0;
    const scoreInterval = setInterval(() => {
        currentScore++;
        scoreValue.textContent = currentScore;
        if (currentScore >= score) {
            clearInterval(scoreInterval);
        }
    }, 20);
    
    // Set circle progress (circumference = 2 * PI * r = 351.86)
    const circumference = 351.86;
    const offset = circumference - (score / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;
    
    // Set color and label based on score
    if (score >= 80) {
        scoreCircle.style.stroke = '#10b981'; // green
        scoreLabel.textContent = 'Excellent ATS Compatibility';
        scoreLabel.className = 'text-green-600 mt-2 font-medium';
    } else if (score >= 60) {
        scoreCircle.style.stroke = '#f59e0b'; // yellow
        scoreLabel.textContent = 'Good - Some Improvements Needed';
        scoreLabel.className = 'text-yellow-600 mt-2 font-medium';
    } else {
        scoreCircle.style.stroke = '#ef4444'; // red
        scoreLabel.textContent = 'Needs Significant Improvement';
        scoreLabel.className = 'text-red-600 mt-2 font-medium';
    }
    
    // Score Breakdown
    const breakdown = analysis.score_breakdown;
    document.getElementById('score-keywords').textContent = breakdown.keyword_optimization;
    document.getElementById('bar-keywords').style.width = breakdown.keyword_optimization + '%';
    document.getElementById('score-formatting').textContent = breakdown.formatting;
    document.getElementById('bar-formatting').style.width = breakdown.formatting + '%';
    document.getElementById('score-structure').textContent = breakdown.structure;
    document.getElementById('bar-structure').style.width = breakdown.structure + '%';
    document.getElementById('score-completeness').textContent = breakdown.completeness;
    document.getElementById('bar-completeness').style.width = breakdown.completeness + '%';
    document.getElementById('score-relevance').textContent = breakdown.relevance;
    document.getElementById('bar-relevance').style.width = breakdown.relevance + '%';
    
    // Recommended Keywords
    const keywordsContainer = document.getElementById('recommended-keywords');
    if (analysis.recommended_keywords.length > 0) {
        keywordsContainer.innerHTML = analysis.recommended_keywords.slice(0, 10).map(kw => {
            const priorityColor = kw.priority === 'high' ? 'red' : 
                                 kw.priority === 'medium' ? 'yellow' : 'blue';
            return `
                <div class="flex items-start gap-2 text-sm">
                    <span class="bg-${priorityColor}-100 text-${priorityColor}-700 px-2 py-1 rounded font-medium">${kw.keyword}</span>
                    <span class="text-gray-600 flex-1">${kw.reason}</span>
                </div>
            `;
        }).join('');
    } else {
        keywordsContainer.innerHTML = '<p class="text-gray-500 text-sm">No specific keyword recommendations</p>';
    }
    
    // Strengths
    const strengthsList = document.getElementById('resume-strengths');
    if (analysis.strengths.length > 0) {
        strengthsList.innerHTML = analysis.strengths.map(s => 
            `<li class="flex items-start">
                <i class="fas fa-check-circle text-green-600 mt-1 mr-2"></i>
                <span class="text-gray-700">${s}</span>
            </li>`
        ).join('');
    } else {
        strengthsList.innerHTML = '<li class="text-gray-500 text-sm">Analysis in progress...</li>';
    }
    
    // Formatting Issues
    const issuesList = document.getElementById('formatting-issues');
    if (analysis.formatting_issues.length > 0) {
        issuesList.innerHTML = analysis.formatting_issues.map(issue => 
            `<li class="flex items-start">
                <i class="fas fa-exclamation-circle text-orange-600 mt-1 mr-2"></i>
                <span class="text-gray-700">${issue}</span>
            </li>`
        ).join('');
    } else {
        issuesList.innerHTML = '<li class="text-green-600"><i class="fas fa-check mr-2"></i>No formatting issues found</li>';
    }
    
    // Improvement Suggestions (top 5 by priority)
    const suggestionsContainer = document.getElementById('improvement-suggestions');
    const topSuggestions = analysis.improvement_suggestions
        .sort((a, b) => a.priority - b.priority)
        .slice(0, 5);
    
    if (topSuggestions.length > 0) {
        suggestionsContainer.innerHTML = topSuggestions.map((s, index) => {
            const impactColor = s.impact === 'high' ? 'green' : 
                               s.impact === 'medium' ? 'yellow' : 'gray';
            return `
                <div class="bg-gray-50 rounded p-3">
                    <div class="flex items-start gap-2">
                        <span class="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-bold">${index + 1}</span>
                        <div class="flex-1">
                            <p class="text-gray-800 font-medium">${s.suggestion}</p>
                            <div class="flex gap-2 mt-1">
                                <span class="text-xs bg-${impactColor}-100 text-${impactColor}-700 px-2 py-0.5 rounded">
                                    ${s.impact.toUpperCase()} Impact
                                </span>
                                <span class="text-xs text-gray-500">${s.category}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        suggestionsContainer.innerHTML = '<p class="text-gray-500 text-sm">No suggestions available</p>';
    }
    
    // Overall Feedback
    document.getElementById('overall-feedback').textContent = analysis.overall_feedback;
    
    showToast('Resume analysis complete!', 'success');
}

