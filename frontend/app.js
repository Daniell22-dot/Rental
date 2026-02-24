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
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Auth Logic
let captchaAnswer = 0;
let regCaptchaAnswer = 0;

function generateCaptcha() {
    const q = document.getElementById('captcha-q');
    if (!q) return;
    const n1 = Math.floor(Math.random() * 10);
    const n2 = Math.floor(Math.random() * 10);
    captchaAnswer = n1 + n2;
    q.textContent = `Human Verification: ${n1} + ${n2} = ?`;
    const input = document.getElementById('captcha-ans');
    if (input) input.value = '';
}

function generateRegCaptcha() {
    const q = document.getElementById('reg-captcha-q');
    if (!q) return;
    const n1 = Math.floor(Math.random() * 10);
    const n2 = Math.floor(Math.random() * 10);
    regCaptchaAnswer = n1 + n2;
    q.textContent = `Security Check: ${n1} + ${n2} = ?`;
    const input = document.getElementById('reg-captcha-ans');
    if (input) input.value = '';
}

async function initApp() {
    console.log("Initializing Tenant App...");
    const token = localStorage.getItem('rms-token');
    if (!token) return;

    try {
        // Fetch User Info
        const res = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const user = await res.json();
            document.getElementById('user-display').textContent = `Account: ${user.email}`;

            // Load Arrears
            const arrearsRes = await fetch('/api/v1/arrears/my', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (arrearsRes.ok) {
                const data = await arrearsRes.json();
                document.getElementById('tenant-arrears').textContent = `Ksh ${data.arrears.toLocaleString()}`;
            }
        }
    } catch (err) {
        console.error('App init error:', err);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-pass').value;
    const userCaptcha = document.getElementById('captcha-ans').value;

    if (parseInt(userCaptcha) !== captchaAnswer) {
        alert('Incorrect human verification code. Please try again.');
        generateCaptcha();
        return;
    }

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
            checkAuth();
        } else {
            alert('Login failed. Please check your credentials.');
        }
    } catch (err) {
        console.error('Login error:', err);
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
        generateCaptcha(); // Ensure captcha is ready when login screen appears
    }
}

// View Management
function showView(viewId) {
    document.querySelectorAll('.content-view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');

    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    document.querySelector(`nav a[onclick*="${viewId}"]`).classList.add('active');

    if (viewId === 'notifications') loadNotifications();
    if (viewId === 'payments') loadPaymentHistory();
}

// Data Fetching
async function loadNotifications() {
    const token = localStorage.getItem('rms-token');
    const res = await fetch('/api/v1/notifications/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const notifications = await res.json();
    const list = document.getElementById('notification-list');
    list.innerHTML = notifications.length ? '' : 'No new notifications.';
    notifications.forEach(n => {
        list.innerHTML += `
            <div class="stat-card" style="margin-bottom: 0.5rem; opacity: ${n.is_read ? '0.6' : '1'}">
                <h4>${n.title}</h4>
                <p>${n.message}</p>
                <small>${new Date(n.created_at).toLocaleString()}</small>
                ${!n.is_read ? `<button onclick="markRead(${n.id})">Mark Read</button>` : ''}
            </div>
        `;
    });
}

// Interaction
async function submitFeedback(event) {
    event.preventDefault();
    const token = localStorage.getItem('rms-token');
    const subject = document.getElementById('fb-subject').value;
    const message = document.getElementById('fb-message').value;

    const res = await fetch('/api/v1/interactions/feedback', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject, message })
    });

    if (res.ok) {
        alert('Feedback submitted. We will get back to you soon!');
        event.target.reset();
    }
}

// Payment
function payViaApp() {
    alert('Please scan the QR code at the counter or use Till Number: 123456');
    // In a real app, show a modal with a QR code
}

async function submitMpesaCode() {
    const code = document.getElementById('mpesa-code').value;
    if (code.length < 8) {
        alert('Please enter a valid MPESA transaction code.');
        return;
    }
}

async function handleRegistration(event) {
    event.preventDefault();
    const first = document.getElementById('reg-first').value.trim();
    const last = document.getElementById('reg-last').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const phone = document.getElementById('reg-phone').value.trim();
    const pass = document.getElementById('reg-pass').value;
    const tos = document.getElementById('reg-tos').checked;
    const userCaptcha = document.getElementById('reg-captcha-ans').value;

    // Validate CAPTCHA
    if (parseInt(userCaptcha) !== regCaptchaAnswer) {
        alert('Incorrect human verification code. Please try again.');
        generateRegCaptcha();
        return;
    }

    // Validate required fields
    if (!first || !last || !email || !phone || !pass) {
        alert('Please fill in all fields.');
        return;
    }

    // Validate TOS acceptance
    if (!tos) {
        alert('You must agree to the Terms of Service.');
        return;
    }

    // Client-side password validation (mirrors backend requirements)
    const passwordErrors = validatePassword(pass);
    if (passwordErrors.length > 0) {
        alert('Password requirements not met:\n• ' + passwordErrors.join('\n• '));
        return;
    }

    // Validate phone format (basic client-side check)
    if (!validatePhoneNumber(phone)) {
        alert('Invalid phone number. Please use Kenya format (e.g., 0712345678 or +254712345678)');
        return;
    }

    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const origText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';

    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: first,
                last_name: last,
                email: email,
                phone: phone,
                password: pass,
                terms_accepted: tos
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('rms-token', data.access_token);
            alert('Registration successful! Redirecting to dashboard...');
            window.location.href = 'index.html';
        } else {
            const error = await response.json();
            // Parse and display backend errors clearly
            let errorMsg = error.detail || 'Unknown error';
            if (typeof errorMsg === 'string' && errorMsg.includes('|')) {
                // Multiple errors separated by |
                const errors = errorMsg.split('|').map(e => e.trim());
                errorMsg = errors.join('\n• ');
            }
            alert(`Registration failed:\n• ${errorMsg}`);
        }
    } catch (err) {
        console.error('Registration error:', err);
        alert('Network error. Please check your connection and try again.');
    } finally {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = origText;
    }
}

// Password validation utility (mirrors backend)
function validatePassword(password) {
    const errors = [];
    
    if (password.length < 8) {
        errors.push('At least 8 characters');
    }
    if (password.length > 72) {
        errors.push('Cannot exceed 72 characters');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('At least one uppercase letter (A-Z)');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('At least one lowercase letter (a-z)');
    }
    if (!/[0-9]/.test(password)) {
        errors.push('At least one number (0-9)');
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};:'",.<>?/\\|`~]/.test(password)) {
        errors.push('At least one special character (!@#$%^&*)');
    }
    
    return errors;
}

// Phone validation utility for Kenya numbers
function validatePhoneNumber(phone) {
    // Pattern: (0 or +254 or 254) followed by 9-10 digits starting with 1-9
    const pattern = /^(\+254|0|254)?([1-9]\d{7,8})$/;
    const cleaned = phone.replace(/[\s\-]/g, '');
    return pattern.test(cleaned);
}

// Global Initialization
window.addEventListener('load', () => {
    initTheme();
    checkAuth();
    // If we're on the login screen, generate the captcha
    const loginScreen = document.getElementById('login-screen');
    if (loginScreen && loginScreen.style.display !== 'none') {
        generateCaptcha();
    }
});