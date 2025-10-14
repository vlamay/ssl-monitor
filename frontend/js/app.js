// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let currentFilter = 'all';
let domains = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadDomains();
    loadStatistics();
    checkAPIHealth();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        loadDomains();
        loadStatistics();
    }, 30000);
    
    // Check API health every 10 seconds
    setInterval(checkAPIHealth, 10000);
    
    // Add Enter key support for domain input
    document.getElementById('domainInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addDomain();
        }
    });
});

// API Health Check
async function checkAPIHealth() {
    const statusDot = document.getElementById('apiStatus');
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusDot.style.background = 'var(--success-color)';
        } else {
            statusDot.style.background = 'var(--warning-color)';
        }
    } catch (error) {
        statusDot.style.background = 'var(--danger-color)';
        console.error('API health check failed:', error);
    }
}

// Load Statistics
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        if (!response.ok) throw new Error('Failed to load statistics');
        
        const stats = await response.json();
        
        document.getElementById('totalDomains').textContent = stats.total_domains;
        document.getElementById('activeDomains').textContent = stats.active_domains;
        document.getElementById('expiringDomains').textContent = stats.domains_expiring_soon;
        document.getElementById('errorDomains').textContent = stats.domains_with_errors + stats.domains_expired;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load Domains
async function loadDomains() {
    const domainList = document.getElementById('domainList');
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains/`);
        if (!response.ok) throw new Error('Failed to load domains');
        
        domains = await response.json();
        
        // Load SSL status for each domain
        const domainsWithStatus = await Promise.all(
            domains.map(async (domain) => {
                try {
                    const statusResponse = await fetch(`${API_BASE_URL}/domains/${domain.id}/ssl-status`);
                    if (statusResponse.ok) {
                        domain.ssl_status = await statusResponse.json();
                    } else {
                        domain.ssl_status = null;
                    }
                } catch (error) {
                    domain.ssl_status = null;
                }
                return domain;
            })
        );
        
        domains = domainsWithStatus;
        renderDomains();
    } catch (error) {
        console.error('Error loading domains:', error);
        domainList.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                Failed to load domains. Please check your API connection.
            </div>
        `;
    }
}

// Render Domains
function renderDomains() {
    const domainList = document.getElementById('domainList');
    
    let filteredDomains = domains;
    if (currentFilter !== 'all') {
        filteredDomains = domains.filter(d => 
            d.ssl_status && d.ssl_status.status === currentFilter
        );
    }
    
    if (filteredDomains.length === 0) {
        domainList.innerHTML = `
            <div class="loading">
                <i class="fas fa-inbox"></i>
                <p>No domains found. Add your first domain above!</p>
            </div>
        `;
        return;
    }
    
    domainList.innerHTML = filteredDomains.map(domain => {
        const status = domain.ssl_status || {};
        const statusClass = status.status || 'error';
        const expiresIn = status.expires_in || 0;
        const lastChecked = status.last_checked ? 
            new Date(status.last_checked).toLocaleString() : 'Never';
        
        return `
            <div class="domain-card ${statusClass}" onclick="showDomainDetails(${domain.id})">
                <div class="domain-header">
                    <div class="domain-name">
                        <i class="fas fa-globe"></i> ${domain.name}
                    </div>
                    <span class="status-badge ${statusClass}">${statusClass}</span>
                </div>
                <div class="domain-info">
                    ${status.is_valid !== undefined ? `
                        <div class="info-row">
                            <i class="fas fa-certificate"></i>
                            <span>Expires in: <strong>${expiresIn} days</strong></span>
                        </div>
                    ` : ''}
                    <div class="info-row">
                        <i class="fas fa-clock"></i>
                        <span>Last checked: <strong>${lastChecked}</strong></span>
                    </div>
                    <div class="info-row">
                        <i class="fas fa-bell"></i>
                        <span>Alert threshold: <strong>${domain.alert_threshold_days} days</strong></span>
                    </div>
                    ${status.error_message ? `
                        <div class="error-message">
                            <i class="fas fa-exclamation-circle"></i> ${status.error_message}
                        </div>
                    ` : ''}
                </div>
                <div class="domain-actions">
                    <button class="btn btn-success" onclick="checkDomain(${domain.id}, event)">
                        <i class="fas fa-sync-alt"></i> Check Now
                    </button>
                    <button class="btn btn-danger" onclick="deleteDomain(${domain.id}, event)">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Add Domain
async function addDomain() {
    const domainInput = document.getElementById('domainInput');
    const thresholdInput = document.getElementById('thresholdInput');
    const domainName = domainInput.value.trim();
    const threshold = parseInt(thresholdInput.value) || 30;
    
    if (!domainName) {
        alert('Please enter a domain name');
        return;
    }
    
    // Basic domain validation
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/;
    if (!domainRegex.test(domainName)) {
        alert('Please enter a valid domain name (e.g., example.com)');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: domainName,
                alert_threshold_days: threshold
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add domain');
        }
        
        const newDomain = await response.json();
        domainInput.value = '';
        thresholdInput.value = '30';
        
        // Trigger immediate SSL check
        await checkDomain(newDomain.id);
        
        // Reload domains
        await loadDomains();
        await loadStatistics();
        
        alert(`Domain ${domainName} added successfully!`);
    } catch (error) {
        console.error('Error adding domain:', error);
        alert(`Error: ${error.message}`);
    }
}

// Check Domain SSL
async function checkDomain(domainId, event) {
    if (event) {
        event.stopPropagation();
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains/${domainId}/check`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error('Failed to check SSL');
        }
        
        // Reload domains to show updated status
        await loadDomains();
        await loadStatistics();
    } catch (error) {
        console.error('Error checking SSL:', error);
        alert(`Error checking SSL: ${error.message}`);
    }
}

// Check All Domains
async function checkAllDomains() {
    const button = event.target;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
    
    try {
        // Check each domain
        for (const domain of domains) {
            await checkDomain(domain.id);
        }
        
        alert('All domains checked successfully!');
    } catch (error) {
        console.error('Error checking all domains:', error);
        alert(`Error: ${error.message}`);
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-sync-alt"></i> Check All';
    }
}

// Delete Domain
async function deleteDomain(domainId, event) {
    if (event) {
        event.stopPropagation();
    }
    
    const domain = domains.find(d => d.id === domainId);
    if (!confirm(`Are you sure you want to delete ${domain.name}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains/${domainId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete domain');
        }
        
        // Reload domains
        await loadDomains();
        await loadStatistics();
        
        alert(`Domain ${domain.name} deleted successfully!`);
    } catch (error) {
        console.error('Error deleting domain:', error);
        alert(`Error: ${error.message}`);
    }
}

// Filter Domains
function filterDomains(filter) {
    currentFilter = filter;
    
    // Update filter button styles
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderDomains();
}

// Show Domain Details
async function showDomainDetails(domainId) {
    const modal = document.getElementById('domainModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    try {
        const response = await fetch(`${API_BASE_URL}/domains/${domainId}`);
        if (!response.ok) throw new Error('Failed to load domain details');
        
        const domain = await response.json();
        
        // Get check history
        const checksResponse = await fetch(`${API_BASE_URL}/domains/${domainId}/checks?limit=10`);
        const checks = checksResponse.ok ? await checksResponse.json() : [];
        
        modalTitle.textContent = `${domain.name} - Details`;
        
        modalBody.innerHTML = `
            <div class="domain-details">
                <h3><i class="fas fa-info-circle"></i> Domain Information</h3>
                <div class="info-row">
                    <i class="fas fa-globe"></i>
                    <span>Domain: <strong>${domain.name}</strong></span>
                </div>
                <div class="info-row">
                    <i class="fas fa-calendar-alt"></i>
                    <span>Added: <strong>${new Date(domain.created_at).toLocaleString()}</strong></span>
                </div>
                <div class="info-row">
                    <i class="fas fa-bell"></i>
                    <span>Alert Threshold: <strong>${domain.alert_threshold_days} days</strong></span>
                </div>
                <div class="info-row">
                    <i class="fas fa-toggle-on"></i>
                    <span>Status: <strong>${domain.is_active ? 'Active' : 'Inactive'}</strong></span>
                </div>
                
                ${domain.latest_check ? `
                    <h3 style="margin-top: 20px;"><i class="fas fa-certificate"></i> Latest SSL Check</h3>
                    <div class="info-row">
                        <i class="fas fa-check-circle"></i>
                        <span>Valid: <strong>${domain.latest_check.is_valid ? 'Yes' : 'No'}</strong></span>
                    </div>
                    <div class="info-row">
                        <i class="fas fa-hourglass-half"></i>
                        <span>Expires in: <strong>${domain.latest_check.expires_in} days</strong></span>
                    </div>
                    ${domain.latest_check.issuer ? `
                        <div class="info-row">
                            <i class="fas fa-building"></i>
                            <span>Issuer: <strong>${domain.latest_check.issuer}</strong></span>
                        </div>
                    ` : ''}
                    ${domain.latest_check.not_valid_after ? `
                        <div class="info-row">
                            <i class="fas fa-calendar-times"></i>
                            <span>Expires on: <strong>${new Date(domain.latest_check.not_valid_after).toLocaleString()}</strong></span>
                        </div>
                    ` : ''}
                ` : '<p style="color: var(--text-secondary); margin-top: 10px;">No SSL checks performed yet.</p>'}
                
                ${checks.length > 0 ? `
                    <h3 style="margin-top: 20px;"><i class="fas fa-history"></i> Check History</h3>
                    <div style="max-height: 200px; overflow-y: auto;">
                        ${checks.map(check => `
                            <div style="padding: 10px; background: var(--bg-color); margin: 5px 0; border-radius: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span>${new Date(check.checked_at).toLocaleString()}</span>
                                    <span class="status-badge ${check.is_valid ? 'healthy' : 'error'}">
                                        ${check.is_valid ? 'Valid' : 'Invalid'}
                                    </span>
                                </div>
                                ${check.expires_in !== null ? `
                                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 5px;">
                                        Expires in ${check.expires_in} days
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading domain details:', error);
        alert(`Error: ${error.message}`);
    }
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('domainModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('domainModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

