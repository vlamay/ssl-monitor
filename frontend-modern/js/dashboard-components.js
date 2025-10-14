/**
 * SSL Monitor Pro - Dashboard Components
 * Reusable UI components for the enhanced dashboard
 */

// Statistics Cards Component
function createStatisticsCards(statistics) {
    const cards = [
        {
            title: 'Total Domains',
            value: statistics.total_domains || 0,
            icon: '🌐',
            color: 'blue',
            description: 'Domains being monitored'
        },
        {
            title: 'Healthy',
            value: (statistics.total_domains || 0) - (statistics.domains_with_errors || 0),
            icon: '✅',
            color: 'green',
            description: 'Certificates in good standing'
        },
        {
            title: 'Expiring Soon',
            value: statistics.domains_expiring_soon || 0,
            icon: '⚠️',
            color: 'yellow',
            description: 'Certificates expiring within 30 days'
        },
        {
            title: 'Problems',
            value: statistics.domains_with_errors || 0,
            icon: '❌',
            color: 'red',
            description: 'Certificates with issues'
        }
    ];

    return cards.map(card => `
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">${card.title}</p>
                    <p class="text-3xl font-bold text-gray-900 mt-2">${card.value}</p>
                    <p class="text-xs text-gray-500 mt-1">${card.description}</p>
                </div>
                <div class="text-4xl">${card.icon}</div>
            </div>
        </div>
    `).join('');
}

// Certificate Timeline Component
function createCertificateTimeline(timeline) {
    if (!timeline || timeline.length === 0) {
        return `
            <div class="text-center py-8">
                <div class="text-4xl mb-4">📅</div>
                <p class="text-gray-600">No certificate expiry data available</p>
                <p class="text-sm text-gray-500 mt-2">Add domains and run SSL checks to see timeline</p>
            </div>
        `;
    }

    return `
        <div class="space-y-3">
            ${timeline.map(item => `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div class="flex items-center space-x-3">
                        <div class="w-3 h-3 rounded-full ${
                            item.status === 'healthy' ? 'bg-green-500' :
                            item.status === 'warning' ? 'bg-yellow-500' :
                            item.status === 'critical' ? 'bg-red-500' :
                            'bg-gray-400'
                        }"></div>
                        <div>
                            <p class="font-medium text-gray-900">${item.domain}</p>
                            <p class="text-sm text-gray-600">Expires: ${item.expiry_date.toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-lg ${
                            item.days_left <= 7 ? 'text-red-600' :
                            item.days_left <= 30 ? 'text-yellow-600' :
                            'text-green-600'
                        }">${item.days_left} days</p>
                        <p class="text-xs text-gray-500">left</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Quick Actions Panel Component
function createQuickActionsPanel() {
    return `
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
            <h3 class="text-lg font-semibold text-blue-900 mb-4">⚡ Quick Actions</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button onclick="quickAction('bulk-check')" 
                        class="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center">
                    <div class="text-2xl mb-2">🔍</div>
                    <div class="font-medium">Check All SSL</div>
                    <div class="text-xs opacity-90">Run checks for all domains</div>
                </button>
                
                <button onclick="quickAction('add-multiple')" 
                        class="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors text-center">
                    <div class="text-2xl mb-2">➕</div>
                    <div class="font-medium">Add Multiple</div>
                    <div class="text-xs opacity-90">Bulk add domains</div>
                </button>
                
                <button onclick="quickAction('export-csv')" 
                        class="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors text-center">
                    <div class="text-2xl mb-2">📊</div>
                    <div class="font-medium">Export CSV</div>
                    <div class="text-xs opacity-90">Download domain list</div>
                </button>
                
                <button onclick="quickAction('refresh-all')" 
                        class="bg-orange-600 text-white px-4 py-3 rounded-lg hover:bg-orange-700 transition-colors text-center">
                    <div class="text-2xl mb-2">🔄</div>
                    <div class="font-medium">Refresh All</div>
                    <div class="text-xs opacity-90">Reload all data</div>
                </button>
            </div>
        </div>
    `;
}

// Search and Filter Bar Component
function createSearchFilterBar() {
    return `
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div class="flex flex-col md:flex-row gap-4">
                <!-- Search -->
                <div class="flex-1">
                    <div class="relative">
                        <input type="text" 
                               id="domain-search"
                               placeholder="Search domains..."
                               class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <!-- Status Filter -->
                <div class="md:w-48">
                    <select id="status-filter" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        <option value="all">All Status</option>
                        <option value="healthy">✅ Healthy</option>
                        <option value="warning">⚠️ Warning</option>
                        <option value="critical">🚨 Critical</option>
                        <option value="error">❌ Error</option>
                        <option value="unknown">❓ Unknown</option>
                    </select>
                </div>
                
                <!-- Sort Options -->
                <div class="md:w-48">
                    <select id="sort-options" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        <option value="name-asc">Name (A-Z)</option>
                        <option value="name-desc">Name (Z-A)</option>
                        <option value="status-asc">Status</option>
                        <option value="days_left-asc">Days Left (Fewest)</option>
                        <option value="days_left-desc">Days Left (Most)</option>
                        <option value="last_checked-desc">Recently Checked</option>
                    </select>
                </div>
                
                <!-- View Toggle -->
                <div class="flex space-x-2">
                    <button id="view-grid" 
                            onclick="toggleView('grid')"
                            class="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                        </svg>
                    </button>
                    <button id="view-list" 
                            onclick="toggleView('list')"
                            class="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Domain Card Component (Grid View)
function createDomainCard(domain) {
    const statusColors = {
        healthy: 'bg-green-100 text-green-800 border-green-200',
        warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        critical: 'bg-red-100 text-red-800 border-red-200',
        error: 'bg-red-100 text-red-800 border-red-200',
        unknown: 'bg-gray-100 text-gray-800 border-gray-200'
    };

    const statusIcons = {
        healthy: '✅',
        warning: '⚠️',
        critical: '🚨',
        error: '❌',
        unknown: '❓'
    };

    const statusClass = statusColors[domain.status] || statusColors.unknown;
    const statusIcon = statusIcons[domain.status] || statusIcons.unknown;

    return `
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow domain-card">
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-900 text-lg mb-1">${domain.name}</h3>
                    <div class="flex items-center space-x-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusClass}">
                            ${statusIcon} ${domain.status || 'unknown'}
                        </span>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="checkDomainSSL(${domain.id})" 
                            class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Check SSL">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                    </button>
                    <button onclick="deleteDomain(${domain.id})" 
                            class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                            title="Delete">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="space-y-2 text-sm text-gray-600">
                ${domain.days_left !== null ? `
                    <div class="flex justify-between">
                        <span>Days until expiry:</span>
                        <span class="font-medium ${
                            domain.days_left <= 7 ? 'text-red-600' :
                            domain.days_left <= 30 ? 'text-yellow-600' :
                            'text-green-600'
                        }">${domain.days_left}</span>
                    </div>
                ` : ''}
                
                ${domain.last_checked ? `
                    <div class="flex justify-between">
                        <span>Last checked:</span>
                        <span class="font-medium">${new Date(domain.last_checked).toLocaleDateString()}</span>
                    </div>
                ` : ''}
                
                <div class="flex justify-between">
                    <span>Added:</span>
                    <span class="font-medium">${new Date(domain.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            
            ${domain.ssl_status && domain.ssl_status.error_message ? `
                <div class="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    <strong>Error:</strong> ${domain.ssl_status.error_message}
                </div>
            ` : ''}
        </div>
    `;
}

// Domain List Item Component (List View)
function createDomainListItem(domain) {
    const statusColors = {
        healthy: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        critical: 'bg-red-100 text-red-800',
        error: 'bg-red-100 text-red-800',
        unknown: 'bg-gray-100 text-gray-800'
    };

    const statusIcons = {
        healthy: '✅',
        warning: '⚠️',
        critical: '🚨',
        error: '❌',
        unknown: '❓'
    };

    const statusClass = statusColors[domain.status] || statusColors.unknown;
    const statusIcon = statusIcons[domain.status] || statusIcons.unknown;

    return `
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow domain-item">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}">
                            ${statusIcon} ${domain.status || 'unknown'}
                        </span>
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-semibold text-gray-900 text-lg">${domain.name}</h3>
                        <div class="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                            ${domain.days_left !== null ? `
                                <span>Expires in <span class="font-medium ${
                                    domain.days_left <= 7 ? 'text-red-600' :
                                    domain.days_left <= 30 ? 'text-yellow-600' :
                                    'text-green-600'
                                }">${domain.days_left} days</span></span>
                            ` : ''}
                            ${domain.last_checked ? `
                                <span>Checked <span class="font-medium">${new Date(domain.last_checked).toLocaleDateString()}</span></span>
                            ` : ''}
                            <span>Added <span class="font-medium">${new Date(domain.created_at).toLocaleDateString()}</span></span>
                        </div>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="checkDomainSSL(${domain.id})" 
                            class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors">
                        Check SSL
                    </button>
                    <button onclick="deleteDomain(${domain.id})" 
                            class="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Bulk Add Domains Modal Component
function createBulkAddModal() {
    return `
        <div id="bulk-add-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden z-50">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full">
                    <div class="flex items-center justify-between p-6 border-b border-gray-200">
                        <h3 class="text-lg font-semibold text-gray-900">Add Multiple Domains</h3>
                        <button onclick="closeBulkAddModal()" class="text-gray-400 hover:text-gray-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="p-6">
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Enter domain names (one per line):
                            </label>
                            <textarea id="bulk-domains-input" 
                                      rows="8"
                                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      placeholder="example.com&#10;google.com&#10;github.com"></textarea>
                        </div>
                        <div class="text-sm text-gray-600 mb-4">
                            <p>• Enter one domain per line</p>
                            <p>• Domains should be in format: example.com</p>
                            <p>• Duplicate domains will be skipped</p>
                        </div>
                        <div class="flex justify-end space-x-3">
                            <button onclick="closeBulkAddModal()" 
                                    class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
                                Cancel
                            </button>
                            <button onclick="submitBulkAdd()" 
                                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                Add Domains
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createStatisticsCards,
        createCertificateTimeline,
        createQuickActionsPanel,
        createSearchFilterBar,
        createDomainCard,
        createDomainListItem,
        createBulkAddModal
    };
}
