/**
 * SSL Monitor Pro - Enhanced Dashboard
 * Advanced statistics, visualizations, and quick actions
 */

class EnhancedDashboard {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.domains = [];
        this.statistics = {};
        this.filteredDomains = [];
        this.searchQuery = '';
        this.statusFilter = 'all';
        this.sortBy = 'name';
        this.sortOrder = 'asc';
    }

    async loadDashboardData() {
        try {
            // Load all data in parallel
            const [domainsData, statisticsData] = await Promise.all([
                this.loadDomains(),
                this.loadStatistics()
            ]);

            this.domains = domainsData;
            this.statistics = statisticsData;
            this.filteredDomains = [...this.domains];

            // Load SSL status for each domain
            await this.loadSSLStatuses();

            return {
                domains: this.domains,
                statistics: this.statistics,
                filteredDomains: this.filteredDomains
            };

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }

    async loadDomains() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/domains/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error loading domains:', error);
            return [];
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/statistics`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error loading statistics:', error);
            return {
                total_domains: 0,
                active_domains: 0,
                domains_with_errors: 0,
                domains_expiring_soon: 0,
                domains_expired: 0
            };
        }
    }

    async loadSSLStatuses() {
        const promises = this.domains.map(async (domain) => {
            try {
                const response = await fetch(`${this.apiBaseUrl}/domains/${domain.id}/ssl-status`);
                if (response.ok) {
                    const sslStatus = await response.json();
                    domain.ssl_status = sslStatus;
                    domain.status = sslStatus.status;
                    domain.days_left = sslStatus.expires_in;
                    domain.last_checked = sslStatus.last_checked;
                } else {
                    domain.ssl_status = null;
                    domain.status = 'unknown';
                    domain.days_left = null;
                    domain.last_checked = null;
                }
            } catch (error) {
                console.log(`No SSL status for domain ${domain.id}`);
                domain.ssl_status = null;
                domain.status = 'unknown';
                domain.days_left = null;
                domain.last_checked = null;
            }
        });

        await Promise.all(promises);
    }

    // Filtering and searching
    filterDomains() {
        let filtered = [...this.domains];

        // Apply search filter
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filtered = filtered.filter(domain => 
                domain.name.toLowerCase().includes(query)
            );
        }

        // Apply status filter
        if (this.statusFilter !== 'all') {
            filtered = filtered.filter(domain => 
                domain.status === this.statusFilter
            );
        }

        // Apply sorting
        filtered.sort((a, b) => {
            let aValue, bValue;
            
            switch (this.sortBy) {
                case 'name':
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
                    break;
                case 'status':
                    aValue = a.status;
                    bValue = b.status;
                    break;
                case 'days_left':
                    aValue = a.days_left || 999;
                    bValue = b.days_left || 999;
                    break;
                case 'last_checked':
                    aValue = new Date(a.last_checked || 0);
                    bValue = new Date(b.last_checked || 0);
                    break;
                default:
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
            }

            if (this.sortOrder === 'desc') {
                return aValue < bValue ? 1 : -1;
            } else {
                return aValue > bValue ? 1 : -1;
            }
        });

        this.filteredDomains = filtered;
        return this.filteredDomains;
    }

    setSearchQuery(query) {
        this.searchQuery = query;
        return this.filterDomains();
    }

    setStatusFilter(status) {
        this.statusFilter = status;
        return this.filterDomains();
    }

    setSorting(sortBy, sortOrder = 'asc') {
        this.sortBy = sortBy;
        this.sortOrder = sortOrder;
        return this.filterDomains();
    }

    // Quick actions
    async bulkCheckSSL() {
        const promises = this.domains.map(async (domain) => {
            try {
                const response = await fetch(`${this.apiBaseUrl}/domains/${domain.id}/check`, {
                    method: 'POST'
                });
                if (response.ok) {
                    return { domain: domain.name, success: true };
                } else {
                    return { domain: domain.name, success: false, error: response.statusText };
                }
            } catch (error) {
                return { domain: domain.name, success: false, error: error.message };
            }
        });

        return await Promise.all(promises);
    }

    async addMultipleDomains(domainNames) {
        const results = [];
        
        for (const domainName of domainNames) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/domains/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name: domainName.trim() }),
                });

                if (response.ok) {
                    const newDomain = await response.json();
                    results.push({ domain: domainName, success: true, data: newDomain });
                } else {
                    const error = await response.json();
                    results.push({ domain: domainName, success: false, error: error.detail });
                }
            } catch (error) {
                results.push({ domain: domainName, success: false, error: error.message });
            }
        }

        return results;
    }

    // Analytics and insights
    getDomainInsights() {
        const insights = {
            total: this.domains.length,
            healthy: 0,
            warning: 0,
            critical: 0,
            error: 0,
            unknown: 0,
            expiringSoon: 0,
            recentlyChecked: 0,
            neverChecked: 0
        };

        const now = new Date();
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

        this.domains.forEach(domain => {
            // Count by status
            switch (domain.status) {
                case 'healthy':
                    insights.healthy++;
                    break;
                case 'warning':
                    insights.warning++;
                    break;
                case 'critical':
                    insights.critical++;
                    break;
                case 'error':
                    insights.error++;
                    break;
                default:
                    insights.unknown++;
            }

            // Count expiring soon (within 30 days)
            if (domain.days_left !== null && domain.days_left <= 30) {
                insights.expiringSoon++;
            }

            // Count check status
            if (!domain.last_checked) {
                insights.neverChecked++;
            } else {
                const lastChecked = new Date(domain.last_checked);
                if (lastChecked > oneDayAgo) {
                    insights.recentlyChecked++;
                }
            }
        });

        return insights;
    }

    getCertificateTimeline() {
        const timeline = [];
        
        this.domains.forEach(domain => {
            if (domain.days_left !== null) {
                const expiryDate = new Date();
                expiryDate.setDate(expiryDate.getDate() + domain.days_left);
                
                timeline.push({
                    domain: domain.name,
                    days_left: domain.days_left,
                    expiry_date: expiryDate,
                    status: domain.status,
                    id: domain.id
                });
            }
        });

        // Sort by days left (ascending)
        timeline.sort((a, b) => a.days_left - b.days_left);

        return timeline.slice(0, 10); // Top 10 expiring soon
    }

    // Export functionality
    exportToCSV() {
        const headers = ['Domain', 'Status', 'Days Left', 'Last Checked', 'Created At'];
        const rows = this.filteredDomains.map(domain => [
            domain.name,
            domain.status || 'unknown',
            domain.days_left || 'N/A',
            domain.last_checked ? new Date(domain.last_checked).toLocaleDateString() : 'Never',
            new Date(domain.created_at).toLocaleDateString()
        ]);

        const csvContent = [headers, ...rows]
            .map(row => row.map(field => `"${field}"`).join(','))
            .join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ssl-domains-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // Real-time updates
    startAutoRefresh(intervalMs = 30000) {
        this.autoRefreshInterval = setInterval(async () => {
            try {
                await this.loadDashboardData();
                this.updateDashboardUI();
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, intervalMs);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    updateDashboardUI() {
        // This will be called by the main dashboard app
        // to update the UI with new data
        if (window.dashboardApp && window.dashboardApp.updateData) {
            window.dashboardApp.updateData({
                domains: this.domains,
                statistics: this.statistics,
                filteredDomains: this.filteredDomains
            });
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EnhancedDashboard };
}
