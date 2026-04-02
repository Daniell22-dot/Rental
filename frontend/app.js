// Main JavaScript for Rental Management System Tenant Portal
// This file handles all frontend logic, including authentication, data fetching, view management, and user interactions.
// let cuurrentUser = null means that we will store the currently logged-in user's information in this variable after successful authentication. This allows us to easily access user details throughout the app without needing to repeatedly fetch them from the server.
let currentUser = null;
let allNotifications = [];
let currentFilter = 'all';

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('rms-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('rms-theme', newTheme);
    updateThemeIcon(newTheme);
    updateSettingsThemeIcon();
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Auth Logic
let captchaAnswer = 0;

function generateCaptcha() {
    const q = document.getElementById('captcha-q');
    if (!q) return;
    const n1 = Math.floor(Math.random() * 10);
    const n2 = Math.floor(Math.random() * 10);
    captchaAnswer = n1 + n2;
    q.textContent = `Verify: ${n1} + ${n2} = ?`;
    const input = document.getElementById('captcha-ans');
    if (input) input.value = '';
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-pass').value;
    const userCaptcha = document.getElementById('captcha-ans').value;

    if (parseInt(userCaptcha) !== captchaAnswer) {
        alert('Incorrect verification code. Please try again.');
        generateCaptcha();
        return;
    }

    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', pass);

        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('rms-token', data.access_token);
            window.location.href = 'index.html';
        } else {
            const error = await response.json();
            alert('Login failed: ' + (error.detail || 'Invalid credentials'));
            generateCaptcha();
        }
    } catch (err) {
        console.error('Login error:', err);
        alert('Network error. Please check your connection.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

function logout() {
    localStorage.removeItem('rms-token');
    window.location.href = 'index.html';
}

function checkAuth() {
    const token = localStorage.getItem('rms-token');
    const authCheck = document.getElementById('auth-check');
    const loginScreen = document.getElementById('login-screen');

    if (token) {
        if (authCheck) authCheck.style.display = 'block';
        if (loginScreen) loginScreen.style.display = 'none';
        initApp();
    } else {
        if (authCheck) authCheck.style.display = 'none';
        if (loginScreen) loginScreen.style.display = 'block';
        generateCaptcha();
    }
}

// Initialize App
async function initApp() {
    console.log("Initializing Tenant App...");
    const token = localStorage.getItem('rms-token');
    if (!token) return;

    try {
        // Get user info
        const userRes = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (userRes.ok) {
            currentUser = await userRes.json();
            document.getElementById('user-display').innerHTML = `<i class="fas fa-user"></i> ${currentUser.first_name} ${currentUser.last_name}`;
            document.getElementById('welcome-message').textContent = `Welcome back, ${currentUser.first_name}!`;
            document.getElementById('profile-name').textContent = `${currentUser.first_name} ${currentUser.last_name}`;
            document.getElementById('profile-email').textContent = currentUser.email;
            document.getElementById('profile-phone').textContent = currentUser.phone || 'Not set';
        }
        
        // Set current date
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        // Load all data
        await Promise.all([
            loadDashboardData(),
            loadNotifications(),
            loadPaymentHistory(),
            loadMaintenanceRequests(),
            loadDocuments(),
            loadFeedbackHistory()
        ]);
        
        loadProfileImage();
        showView('home');
    } catch (err) {
        console.error('App init error:', err);
    }
}

// Dashboard Data
async function loadDashboardData() {
    const token = localStorage.getItem('rms-token');
    
    try {
        // Load arrears
        const arrearsRes = await fetch('/api/v1/arrears/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (arrearsRes.ok) {
            const data = await arrearsRes.json();
            document.getElementById('tenant-arrears').textContent = `Ksh ${data.arrears.toLocaleString()}`;
        }
        
        // Load monthly rent
        const propertyRes = await fetch('/api/v1/properties/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (propertyRes.ok) {
            const properties = await propertyRes.json();
            if (properties && properties.length > 0) {
                document.getElementById('monthly-rent').textContent = `Ksh ${properties[0].monthly_rent?.toLocaleString() || '0'}`;
            }
        }
        
        // Set next due date (5th of next month)
        const today = new Date();
        const nextDue = new Date(today.getFullYear(), today.getMonth() + 1, 5);
        document.getElementById('next-due').textContent = nextDue.toLocaleDateString();
        
    } catch (err) {
        console.error('Error loading dashboard:', err);
    }
}

// View Management
function showView(viewId) {
    const views = ['home', 'property', 'payments', 'maintenance', 'notifications', 'documents', 'feedback', 'settings'];
    
    views.forEach(id => {
        const view = document.getElementById(id);
        if (view) {
            view.classList.remove('active');
            view.style.display = 'none';
        }
    });
    
    const selectedView = document.getElementById(viewId);
    if (selectedView) {
        selectedView.classList.add('active');
        selectedView.style.display = 'block';
    }

    // Update navigation
    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = Array.from(document.querySelectorAll('nav a')).find(link => 
        link.getAttribute('onclick') && link.getAttribute('onclick').includes(viewId)
    );
    if (activeLink) activeLink.classList.add('active');

    // Refresh data based on view
    if (viewId === 'notifications') loadNotifications();
    if (viewId === 'payments') loadPaymentHistory();
    if (viewId === 'maintenance') loadMaintenanceRequests();
    if (viewId === 'documents') loadDocuments();
    if (viewId === 'feedback') loadFeedbackHistory();
}

// Notifications
async function loadNotifications() {
    const token = localStorage.getItem('rms-token');
    const list = document.getElementById('notification-list');
    
    try {
        const res = await fetch('/api/v1/notifications/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        allNotifications = await res.json();
        
        updateNotificationBadge();
        renderNotifications(currentFilter);
    } catch (err) {
        console.error('Error loading notifications:', err);
        if (list) list.innerHTML = '<div class="card">Error loading notifications.</div>';
    }
}

function renderNotifications(filter) {
    const list = document.getElementById('notification-list');
    if (!list) return;
    
    let filtered = allNotifications;
    if (filter === 'unread') {
        filtered = allNotifications.filter(n => !n.is_read);
    }
    
    if (filtered.length === 0) {
        list.innerHTML = '<div class="card">No notifications found.</div>';
        return;
    }
    
    list.innerHTML = filtered.map(notif => `
        <div class="notification-item ${!notif.is_read ? 'unread' : ''}" onclick="markNotificationRead(${notif.id})">
            <div class="notification-content">
                <h4>${escapeHtml(notif.title)}</h4>
                <p>${escapeHtml(notif.message)}</p>
                <div class="notification-time">${new Date(notif.created_at).toLocaleString()}</div>
            </div>
            ${!notif.is_read ? '<i class="fas fa-circle" style="color: var(--accent); font-size: 0.75rem;"></i>' : ''}
        </div>
    `).join('');
}

function filterNotifications(filter) {
    currentFilter = filter;
    renderNotifications(filter);
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(filter)) {
            btn.classList.add('active');
        }
    });
}

async function markNotificationRead(id) {
    const token = localStorage.getItem('rms-token');
    try {
        await fetch(`/api/v1/notifications/${id}/read`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        await loadNotifications();
    } catch (err) {
        console.error('Error marking notification read:', err);
    }
}

async function markAllRead() {
    const token = localStorage.getItem('rms-token');
    try {
        for (const notif of allNotifications.filter(n => !n.is_read)) {
            await fetch(`/api/v1/notifications/${notif.id}/read`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        }
        await loadNotifications();
    } catch (err) {
        console.error('Error marking all read:', err);
    }
}

function updateNotificationBadge() {
    const unreadCount = allNotifications.filter(n => !n.is_read).length;
    const badge = document.getElementById('notif-badge');
    if (badge) {
        if (unreadCount > 0) {
            badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Payment History
async function loadPaymentHistory() {
    const token = localStorage.getItem('rms-token');
    const tbody = document.getElementById('payment-history-list');
    
    try {
        const res = await fetch('/api/v1/payments/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const payments = await res.json();
        
        if (!payments || payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No payment history found.</td></tr>';
            return;
        }
        
        tbody.innerHTML = payments.map(payment => `
            <tr>
                <td>${new Date(payment.payment_date).toLocaleDateString()}</td>
                <td>Ksh ${payment.amount.toLocaleString()}</td>
                <td>${payment.payment_method || 'M-Pesa'}</td>
                <td><span class="status-badge status-${payment.status}">${payment.status}</span></td>
                <td>${payment.receipt_url ? '<a href="#" onclick="downloadReceipt(' + payment.id + ')">Download</a>' : '-'}</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Error loading payments:', err);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Error loading payment history.</td></tr>';
    }
}

// Maintenance Requests
async function loadMaintenanceRequests() {
    const token = localStorage.getItem('rms-token');
    const container = document.getElementById('maintenance-list');
    
    try {
        const res = await fetch('/api/v1/maintenance/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const requests = await res.json();
        
        if (!requests || requests.length === 0) {
            container.innerHTML = '<div class="card">No maintenance requests found.</div>';
            return;
        }
        
        container.innerHTML = requests.map(req => `
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <h4>${escapeHtml(req.type)}</h4>
                    <span class="status-badge status-${req.status}">${req.status}</span>
                </div>
                <p>${escapeHtml(req.description)}</p>
                <small>Submitted: ${new Date(req.created_at).toLocaleDateString()}</small>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading maintenance:', err);
        container.innerHTML = '<div class="card">Error loading maintenance requests.</div>';
    }
}

function showMaintenanceModal() {
    document.getElementById('maintenance-modal').style.display = 'flex';
}

function closeMaintenanceModal() {
    document.getElementById('maintenance-modal').style.display = 'none';
}

async function createMaintenanceRequest(event) {
    event.preventDefault();
    const token = localStorage.getItem('rms-token');
    
    const requestData = {
        type: document.getElementById('maint-type').value,
        description: document.getElementById('maint-description').value,
        preferred_time: document.getElementById('maint-time').value
    };
    
    try {
        const res = await fetch('/api/v1/maintenance', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (res.ok) {
            alert('Maintenance request submitted successfully!');
            closeMaintenanceModal();
            document.getElementById('maintenance-form').reset();
            loadMaintenanceRequests();
        } else {
            alert('Failed to submit request. Please try again.');
        }
    } catch (err) {
        console.error('Error creating request:', err);
        alert('Network error. Please try again.');
    }
}

// Documents
async function loadDocuments() {
    const token = localStorage.getItem('rms-token');
    const container = document.getElementById('documents-list');
    
    try {
        const res = await fetch('/api/v1/documents/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const documents = await res.json();
        
        if (!documents || documents.length === 0) {
            container.innerHTML = '<div class="card">No documents available.</div>';
            return;
        }
        
        container.innerHTML = documents.map(doc => `
            <div class="card">
                <i class="fas fa-file-pdf" style="font-size: 2rem; color: var(--danger);"></i>
                <h4>${escapeHtml(doc.title)}</h4>
                <small>Uploaded: ${new Date(doc.uploaded_at).toLocaleDateString()}</small>
                <button onclick="downloadDocument(${doc.id})" class="btn-secondary" style="margin-top: 0.5rem;">Download</button>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading documents:', err);
        container.innerHTML = '<div class="card">Error loading documents.</div>';
    }
}

// Feedback
async function submitFeedback(event) {
    event.preventDefault();
    const token = localStorage.getItem('rms-token');
    
    const feedbackData = {
        subject: document.getElementById('fb-subject').value,
        category: document.getElementById('fb-category').value,
        message: document.getElementById('fb-message').value,
        urgency: document.getElementById('fb-urgency').value
    };
    
    try {
        const res = await fetch('/api/v1/interactions/feedback', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        });
        
        if (res.ok) {
            alert('Feedback submitted successfully!');
            event.target.reset();
            loadFeedbackHistory();
        } else {
            alert('Failed to submit feedback. Please try again.');
        }
    } catch (err) {
        console.error('Error submitting feedback:', err);
        alert('Network error. Please try again.');
    }
}

async function loadFeedbackHistory() {
    const token = localStorage.getItem('rms-token');
    const container = document.getElementById('feedback-history-list');
    
    try {
        const res = await fetch('/api/v1/interactions/my-feedback', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const feedbacks = await res.json();
        
        if (!feedbacks || feedbacks.length === 0) {
            container.innerHTML = '<div class="card">No feedback history.</div>';
            return;
        }
        
        container.innerHTML = feedbacks.map(fb => `
            <div class="card" style="margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>${escapeHtml(fb.subject)}</strong>
                    <span class="status-badge">${fb.status || 'Pending'}</span>
                </div>
                <p>${escapeHtml(fb.message)}</p>
                <small>${new Date(fb.created_at).toLocaleDateString()}</small>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading feedback:', err);
    }
}

// Payment Methods
function payViaMpesa() {
    alert('M-Pesa Payment\n\nPaybill: 123456\nAccount: Your phone number\nAmount: Monthly rent amount\n\nWe will confirm your payment within 24 hours.');
}

function payViaCard() {
    alert('Card payment integration - Coming soon!');
}

function showQRCode() {
    alert('Scan QR code at the rental office to make payment.');
}

async function submitMpesaCode() {
    const code = document.getElementById('mpesa-code').value;
    if (code.length < 8) {
        alert('Please enter a valid M-Pesa transaction code.');
        return;
    }
    
    const token = localStorage.getItem('rms-token');
    try {
        const res = await fetch('/api/v1/payments/verify-mpesa', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transaction_code: code })
        });
        
        if (res.ok) {
            alert('Payment verified successfully!');
            document.getElementById('mpesa-code').value = '';
            loadPaymentHistory();
            loadDashboardData();
        } else {
            alert('Payment verification failed. Please contact admin.');
        }
    } catch (err) {
        console.error('Error verifying payment:', err);
        alert('Network error. Please try again.');
    }
}

// Profile Management
function uploadProfileImage(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.size > 2 * 1024 * 1024) {
            alert('File size must be less than 2MB');
            return;
        }
        
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const avatar = document.getElementById('profile-avatar');
            if (avatar) {
                avatar.src = e.target.result;
                localStorage.setItem('rms-profile-image', e.target.result);
            }
        };
        reader.readAsDataURL(file);
    }
}

function loadProfileImage() {
    const savedImage = localStorage.getItem('rms-profile-image');
    if (savedImage) {
        const avatar = document.getElementById('profile-avatar');
        if (avatar) avatar.src = savedImage;
    }
}

function editProfile() {
    alert('Profile editing - Coming soon!');
}

function changePassword() {
    alert('Password change - This would open a secure password change form.');
}

function enable2FA() {
    alert('Two-factor authentication setup - Coming soon!');
}

function updateNotificationPref(type, enabled) {
    console.log(`Notification ${type}: ${enabled}`);
    // API call to update preferences
}

function exportMyData() {
    alert('Data export - This would generate a PDF of your rental history.');
}

function requestAccountDeletion() {
    if (confirm('Are you sure you want to request account deletion? This action cannot be undone.')) {
        alert('Account deletion request submitted. Admin will contact you.');
    }
}

function refreshData() {
    initApp();
}

function forgotPassword() {
    alert('Password reset link will be sent to your email.');
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateSettingsThemeIcon() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const icon = document.getElementById('settings-theme-icon');
    if (icon) {
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    checkAuth();
});

window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Global error:', {msg, url, lineNo, error});
    return false;
};