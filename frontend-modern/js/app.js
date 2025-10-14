// SSL Monitor Pro - API Client
// Configuration
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://ssl-monitor-api.onrender.com';

// API Client Class
class SSLMonitorAPI {
    constructor(baseURL = API_BASE) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Health Check
    async healthCheck() {
        return this.request('/health');
    }

    // Domains
    async getDomains() {
        try {
            const response = await fetch(`${this.baseURL}/domains/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            console.log('Domains API response:', data);
            return data;
        } catch (error) {
            console.error('getDomains error:', error);
            throw error;
        }
    }

    async getDomain(domainId) {
        return this.request(`/domains/${domainId}`);
    }

    async addDomain(domainName) {
        try {
            const response = await fetch(`${this.baseURL}/domains/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: domainName }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            console.log('Add domain API response:', data);
            return data;
        } catch (error) {
            console.error('addDomain error:', error);
            throw error;
        }
    }

    async updateDomain(domainId, updates) {
        return this.request(`/domains/${domainId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    async deleteDomain(domainId) {
        return this.request(`/domains/${domainId}`, {
            method: 'DELETE',
        });
    }

    // SSL Checks
    async checkSSL(domainId) {
        return this.request(`/domains/${domainId}/check`, {
            method: 'POST',
        });
    }

    async getSSLStatus(domainId) {
        return this.request(`/domains/${domainId}/ssl-status`);
    }

    async getSSLHistory(domainId, limit = 50) {
        return this.request(`/domains/${domainId}/checks?limit=${limit}`);
    }

    // Statistics
    async getStatistics() {
        try {
            const response = await fetch(`${this.baseURL}/statistics`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            console.log('Statistics API response:', data);
            return data;
        } catch (error) {
            console.error('getStatistics error:', error);
            throw error;
        }
    }

    // Billing
    async getBillingPlans() {
        return this.request('/billing/plans');
    }
}

// Initialize API client
const api = new SSLMonitorAPI();

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

function getStatusColor(status) {
    const colors = {
        healthy: 'green',
        warning: 'yellow',
        critical: 'red',
        error: 'gray',
    };
    return colors[status] || 'gray';
}

function getStatusIcon(status) {
    const icons = {
        healthy: '✅',
        warning: '⚠️',
        critical: '🚨',
        error: '❌',
    };
    return icons[status] || '❓';
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transition-all transform translate-x-0 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { api, SSLMonitorAPI, formatDate, getStatusColor, getStatusIcon, showNotification };
}

