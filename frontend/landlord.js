// landlord portal
// This JavaScript file manages the landlord dashboard, including data fetching, view management, and user interactions for landlords.
let revenueChart = null;

    
async function initLandlordApp() {
    const token = localStorage.getItem('rms-landlord-token');
    if (!token) {
        window.location.href = 'landlord-login.html';
        return;
    }

    await loadDashboardData();
    await loadProperties();
    await loadTenants();
    await loadPayments();
    await loadMaintenanceRequests();
}

async function loadDashboardData() {
    const token = localStorage.getItem('rms-landlord-token');
    
    try {
        const metricsRes = await fetch('/api/v1/admin/metrics', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const metrics = await metricsRes.json();
        
        document.getElementById('total-properties').textContent = metrics.total_properties || 0;
        document.getElementById('total-tenants').textContent = metrics.total_tenants || 0;
        document.getElementById('monthly-revenue').textContent = `Ksh ${(metrics.total_revenue || 0).toLocaleString()}`;
        document.getElementById('overdue-amount').textContent = `Ksh ${(metrics.overdue_amount || 0).toLocaleString()}`;
        
        // Load recent payments for the dashboard
        // This will show the 5 most recent payments on the dashboard
        const paymentsRes = await fetch('/api/v1/payments/recent', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const payments = await paymentsRes.json();
        
        const tableBody = document.getElementById('recent-payments-table');
        if (payments && payments.length > 0) {
            tableBody.innerHTML = payments.slice(0, 5).map(p => `
                <tr>
                    <td>${p.tenant_name || 'N/A'}</td>
                    <td>${p.property_name || 'N/A'}</td>
                    <td>Ksh ${p.amount.toLocaleString()}</td>
                    <td>${new Date(p.payment_date).toLocaleDateString()}</td>
                    <td><span class="status-badge status-${p.status}">${p.status}</span></td>
                </tr>
            `).join('');
        }
        
        // Initialize chart
        initRevenueChart();
        
    } catch (err) {
        console.error('Error loading dashboard:', err);
    }
}

function initRevenueChart() {
    const ctx = document.getElementById('revenue-chart')?.getContext('2d');
    if (!ctx) return;
    
    if (revenueChart) revenueChart.destroy();
    
    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue (KES)',
                data: [0, 0, 0, 0, 0, 0],
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

async function loadProperties() {
    const token = localStorage.getItem('rms-landlord-token');
    const container = document.getElementById('properties-list');
    
    try {
        const res = await fetch('/api/v1/properties/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const properties = await res.json();
        
        if (!properties || properties.length === 0) {
            container.innerHTML = '<div class="card">No properties found.</div>';
            return;
        }
        
        container.innerHTML = properties.map(prop => `
            <div class="card property-card">
                <h4>${escapeHtml(prop.name)}</h4>
                <p>${escapeHtml(prop.address)}</p>
                <p>Units: ${prop.units || 0}</p>
                <p>Occupancy: ${prop.occupancy_rate || 0}%</p>
                <button onclick="editProperty(${prop.id})" class="btn-secondary">Edit</button>
                <button onclick="viewPropertyDetails(${prop.id})" class="btn-primary">View Details</button>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading properties:', err);
        container.innerHTML = '<div class="card">Error loading properties.</div>';
    }
}

async function loadTenants() {
    const token = localStorage.getItem('rms-landlord-token');
    const tbody = document.getElementById('tenants-table-body');
    
    try {
        const res = await fetch('/api/v1/tenants/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const tenants = await res.json();
        
        if (!tenants || tenants.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No tenants found.</td></tr>';
            return;
        }
        
        tbody.innerHTML = tenants.map(tenant => `
            <tr>
                <td>${escapeHtml(tenant.first_name)} ${escapeHtml(tenant.last_name)}</td>
                <td>${escapeHtml(tenant.property_name || 'N/A')}</td>
                <td>${tenant.phone || 'N/A'}</td>
                <td>Ksh ${(tenant.monthly_rent || 0).toLocaleString()}</td>
                <td><span class="status-badge status-${tenant.status}">${tenant.status}</span></td>
                <td>
                    <button onclick="viewTenantDetails(${tenant.id})" class="icon-btn"><i class="fas fa-eye"></i></button>
                    <button onclick="sendMessageToTenant(${tenant.id})" class="icon-btn"><i class="fas fa-envelope"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Error loading tenants:', err);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Error loading tenants.</td></tr>';
    }
}

async function loadPayments() {
    const token = localStorage.getItem('rms-landlord-token');
    const tbody = document.getElementById('all-payments-table');
    
    try {
        const res = await fetch('/api/v1/payments/all', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const payments = await res.json();
        
        if (!payments || payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No payments found.</td></tr>';
            return;
        }
        
        tbody.innerHTML = payments.map(payment => `
            <tr>
                <td>${escapeHtml(payment.tenant_name)}</td>
                <td>Ksh ${payment.amount.toLocaleString()}</td>
                <td>${new Date(payment.payment_date).toLocaleDateString()}</td>
                <td>${payment.payment_method || 'M-Pesa'}</td>
                <td><span class="status-badge status-${payment.status}">${payment.status}</span></td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Error loading payments:', err);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Error loading payments.</td></tr>';
    }
}

async function loadMaintenanceRequests() {
    const token = localStorage.getItem('rms-landlord-token');
    const container = document.getElementById('maintenance-requests-list');
    
    try {
        const res = await fetch('/api/v1/maintenance/all', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const requests = await res.json();
        
        if (!requests || requests.length === 0) {
            container.innerHTML = '<div class="card">No maintenance requests.</div>';
            return;
        }
        
        container.innerHTML = requests.map(req => `
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between;">
                    <h4>${escapeHtml(req.type)} - Unit ${req.unit_number}</h4>
                    <select onchange="updateRequestStatus(${req.id}, this.value)" class="status-select">
                        <option value="pending" ${req.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="in_progress" ${req.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${req.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </div>
                <p><strong>From:</strong> ${escapeHtml(req.tenant_name)}</p>
                <p>${escapeHtml(req.description)}</p>
                <small>Submitted: ${new Date(req.created_at).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading maintenance:', err);
        container.innerHTML = '<div class="card">Error loading maintenance requests.</div>';
    }
}

function showLandlordView(viewId) {
    const views = ['dashboard', 'properties', 'tenants', 'payments', 'maintenance', 'reports'];
    
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
    
    document.getElementById('view-title').textContent = viewId.charAt(0).toUpperCase() + viewId.slice(1);
    
    // Refresh data
    if (viewId === 'dashboard') loadDashboardData();
    if (viewId === 'properties') loadProperties();
    if (viewId === 'tenants') loadTenants();
    if (viewId === 'payments') loadPayments();
    if (viewId === 'maintenance') loadMaintenanceRequests();
}

function addProperty() {
    alert('Add property form - Coming soon!');
}

function editProperty(id) {
    alert(`Edit property ${id} - Coming soon!`);
}

function viewPropertyDetails(id) {
    alert(`View property ${id} details - Coming soon!`);
}

function viewTenantDetails(id) {
    alert(`View tenant ${id} details - Coming soon!`);
}

function sendMessageToTenant(id) {
    alert(`Send message to tenant - Coming soon!`);
}

async function updateRequestStatus(requestId, status) {
    const token = localStorage.getItem('rms-landlord-token');
    try {
        await fetch(`/api/v1/maintenance/${requestId}/status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });
        alert('Status updated successfully!');
        loadMaintenanceRequests();
    } catch (err) {
        console.error('Error updating status:', err);
        alert('Failed to update status.');
    }
}

function generateReport() {
    const type = document.getElementById('report-type').value;
    alert(`Generating ${type} report - Coming soon!`);
}

function logout() {
    localStorage.removeItem('rms-landlord-token');
    localStorage.removeItem('rms-landlord-role');
    window.location.href = 'landlord-login.html';
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('rms-theme', newTheme);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('rms-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    initLandlordApp();
});