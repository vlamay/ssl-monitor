// 🌍 Internationalization (i18n) for SSL Monitor Pro
// Supports: EN, DE, FR, ES, IT, RU

class I18n {
    constructor() {
        this.currentLanguage = this.getStoredLanguage() || 'en';
        this.translations = {};
        this.apiBaseUrl = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : 'https://ssl-monitor-api.onrender.com';
        this.authToken = this.getAuthToken();
        this.syncInProgress = false;
        this.init();
    }
    
    // Get auth token from localStorage
    getAuthToken() {
        return localStorage.getItem('ssl-monitor-token');
    }
    
    // Check if user is logged in
    isLoggedIn() {
        return !!this.authToken;
    }

    // Supported languages
    get supportedLanguages() {
        return {
            'en': { name: 'English', flag: '🇬🇧', code: 'en' },
            'de': { name: 'Deutsch', flag: '🇩🇪', code: 'de' },
            'fr': { name: 'Français', flag: '🇫🇷', code: 'fr' },
            'es': { name: 'Español', flag: '🇪🇸', code: 'es' },
            'it': { name: 'Italiano', flag: '🇮🇹', code: 'it' },
            'ru': { name: 'Русский', flag: '🇷🇺', code: 'ru' }
        };
    }

    // Initialize translations
    async init() {
        await this.loadTranslations();
        await this.loadUserPreferences(); // NEW: Load from server if logged in
        this.updatePageLanguage();
        this.createLanguageSwitcher();
    }
    
    // NEW: Load user preferences from server
    async loadUserPreferences() {
        if (!this.isLoggedIn()) {
            console.log('[i18n] User not logged in, using localStorage');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/user/profile`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                const serverLanguage = data.user.preferred_language;
                
                // Sync server language to local
                if (serverLanguage && serverLanguage !== this.currentLanguage) {
                    console.log(`[i18n] Syncing language from server: ${serverLanguage}`);
                    this.currentLanguage = serverLanguage;
                    localStorage.setItem('ssl-monitor-language', serverLanguage);
                }
            } else {
                console.warn('[i18n] Failed to load user preferences:', response.status);
            }
        } catch (error) {
            console.warn('[i18n] Error loading user preferences:', error);
        }
    }

    // Load translation files
    async loadTranslations() {
        try {
            for (const lang of Object.keys(this.supportedLanguages)) {
                const response = await fetch(`/js/locales/${lang}.json`);
                if (response.ok) {
                    this.translations[lang] = await response.json();
                }
            }
        } catch (error) {
            console.warn('Failed to load translations:', error);
            // Fallback to embedded translations
            this.translations = this.getEmbeddedTranslations();
        }
    }

    // Get translation for current language
    t(key, params = {}) {
        const translation = this.getNestedTranslation(this.translations[this.currentLanguage], key) ||
                          this.getNestedTranslation(this.translations['en'], key) ||
                          key;

        return this.interpolate(translation, params);
    }

    // Get nested translation (e.g., 'hero.title')
    getNestedTranslation(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }

    // Interpolate parameters in translation
    interpolate(text, params) {
        return text.replace(/\{\{(\w+)\}\}/g, (match, key) => params[key] || match);
    }

    // Change language
    async setLanguage(lang) {
        if (this.supportedLanguages[lang]) {
            const oldLanguage = this.currentLanguage;
            this.currentLanguage = lang;
            localStorage.setItem('ssl-monitor-language', lang);
            this.updatePageLanguage();
            this.updateLanguageSwitcher();
            
            // NEW: Sync to server if logged in
            await this.syncLanguageToServer(lang, oldLanguage);
            
            // NEW: Track language change event
            this.trackLanguageChange(oldLanguage, lang);
        }
    }
    
    // NEW: Sync language preference to server
    async syncLanguageToServer(newLanguage, oldLanguage) {
        if (!this.isLoggedIn() || this.syncInProgress) {
            return;
        }
        
        this.syncInProgress = true;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/user/language`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    language: newLanguage,
                    device_type: this.getDeviceType()
                })
            });
            
            if (response.ok) {
                console.log(`[i18n] Language synced to server: ${newLanguage}`);
            } else {
                console.warn('[i18n] Failed to sync language to server:', response.status);
                // Fallback: localStorage still works
            }
        } catch (error) {
            console.warn('[i18n] Error syncing language to server:', error);
            // Graceful degradation: continue with localStorage
        } finally {
            this.syncInProgress = false;
        }
    }
    
    // NEW: Track language change for analytics
    trackLanguageChange(oldLanguage, newLanguage) {
        if (window.gtag) {
            gtag('event', 'language_change', {
                'event_category': 'i18n',
                'event_label': `${oldLanguage} → ${newLanguage}`,
                'old_language': oldLanguage,
                'new_language': newLanguage,
                'device_type': this.getDeviceType()
            });
        }
        
        console.log(`[i18n] Language changed: ${oldLanguage} → ${newLanguage}`);
    }
    
    // NEW: Detect device type
    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }

    // Get stored language
    getStoredLanguage() {
        return localStorage.getItem('ssl-monitor-language');
    }

    // Update page language
    updatePageLanguage() {
        document.documentElement.lang = this.currentLanguage;
        
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translation;
            } else if (element.tagName === 'INPUT' && element.type !== 'submit') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update title and meta description
        document.title = this.t('meta.title');
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) {
            metaDesc.content = this.t('meta.description');
        }
    }

    // Create language switcher
    createLanguageSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <div class="language-current">
                <span class="language-flag">${this.supportedLanguages[this.currentLanguage].flag}</span>
                <span class="language-name">${this.supportedLanguages[this.currentLanguage].name}</span>
                <span class="language-arrow">▼</span>
            </div>
            <div class="language-dropdown">
                ${Object.entries(this.supportedLanguages)
                    .map(([code, lang]) => `
                        <div class="language-option ${code === this.currentLanguage ? 'active' : ''}" 
                             data-lang="${code}">
                            <span class="language-flag">${lang.flag}</span>
                            <span class="language-name">${lang.name}</span>
                        </div>
                    `).join('')}
            </div>
        `;

        // Add click handlers
        switcher.querySelector('.language-current').addEventListener('click', () => {
            switcher.classList.toggle('open');
        });

        switcher.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', () => {
                const lang = option.dataset.lang;
                this.setLanguage(lang);
                switcher.classList.remove('open');
            });
        });

        // Add to header
        const header = document.querySelector('header');
        if (header) {
            header.appendChild(switcher);
        }
    }

    // Update language switcher
    updateLanguageSwitcher() {
        const current = document.querySelector('.language-current');
        if (current) {
            current.innerHTML = `
                <span class="language-flag">${this.supportedLanguages[this.currentLanguage].flag}</span>
                <span class="language-name">${this.supportedLanguages[this.currentLanguage].name}</span>
                <span class="language-arrow">▼</span>
            `;
        }

        document.querySelectorAll('.language-option').forEach(option => {
            option.classList.toggle('active', option.dataset.lang === this.currentLanguage);
        });
    }

    // Embedded translations (fallback)
    getEmbeddedTranslations() {
        return {
            en: {
                'hero.title': 'Monitor SSL Certificates',
                'hero.subtitle': 'Get instant alerts when your SSL certificates are about to expire',
                'hero.description': 'Never miss an SSL certificate expiration again. Get proactive notifications via email, SMS, or Slack.',
                'hero.cta': 'Start Free Trial',
                'hero.trial': '7-day free trial • No credit card required • Cancel anytime',
                'pricing.title': 'Choose Your Plan',
                'features.title': 'Why Choose SSL Monitor Pro?',
                'meta.title': 'SSL Certificate Monitor - Never Miss an Expiration',
                'meta.description': 'Professional SSL certificate monitoring with instant alerts. 7-day free trial, no credit card required.'
            },
            de: {
                'hero.title': 'SSL-Zertifikate überwachen',
                'hero.subtitle': 'Erhalten Sie sofortige Benachrichtigungen, wenn Ihre SSL-Zertifikate ablaufen',
                'hero.description': 'Verpassen Sie nie wieder ein ablaufendes SSL-Zertifikat. Erhalten Sie proaktive Benachrichtigungen per E-Mail, SMS oder Slack.',
                'hero.cta': 'Kostenlose Testversion starten',
                'hero.trial': '7-tägige kostenlose Testversion • Keine Kreditkarte erforderlich • Jederzeit kündbar',
                'pricing.title': 'Wählen Sie Ihren Plan',
                'features.title': 'Warum SSL Monitor Pro wählen?',
                'meta.title': 'SSL-Zertifikat-Monitor - Verpassen Sie nie ein Ablaufdatum',
                'meta.description': 'Professionelle SSL-Zertifikat-Überwachung mit sofortigen Benachrichtigungen. 7-tägige kostenlose Testversion, keine Kreditkarte erforderlich.'
            },
            ru: {
                'hero.title': 'Мониторинг SSL-сертификатов',
                'hero.subtitle': 'Получайте мгновенные уведомления об истечении SSL-сертификатов',
                'hero.description': 'Никогда не пропускайте истечение SSL-сертификата. Получайте упреждающие уведомления по email, SMS или Slack.',
                'hero.cta': 'Начать бесплатный пробный период',
                'hero.trial': '7-дневный бесплатный пробный период • Без кредитной карты • Отмена в любое время',
                'pricing.title': 'Выберите свой план',
                'features.title': 'Почему выбирают SSL Monitor Pro?',
                'meta.title': 'Мониторинг SSL-сертификатов - Никогда не пропускайте истечение',
                'meta.description': 'Профессиональный мониторинг SSL-сертификатов с мгновенными уведомлениями. 7-дневный бесплатный пробный период, без кредитной карты.'
            }
        };
    }
}

// Initialize i18n when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.i18n = new I18n();
});
