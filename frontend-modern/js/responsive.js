// Responsive & Performance Detection System
class DeviceCapabilities {
    constructor() {
        this.capabilities = this.detect();
    }

    detect() {
        return {
            // Screen
            isMobile: window.innerWidth < 768,
            isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
            isDesktop: window.innerWidth >= 1024,
            
            // WebGL
            webgl: this.detectWebGL(),
            webgl2: this.detectWebGL2(),
            
            // Touch
            touch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
            
            // Network
            connection: this.getConnectionType(),
            
            // Battery
            battery: 'getBattery' in navigator,
            
            // Worker
            webWorker: typeof Worker !== 'undefined',
            
            // Performance
            deviceMemory: navigator.deviceMemory || 4,
            hardwareConcurrency: navigator.hardwareConcurrency || 4
        };
    }

    detectWebGL() {
        try {
            const canvas = document.createElement('canvas');
            return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
        } catch (e) {
            return false;
        }
    }

    detectWebGL2() {
        try {
            const canvas = document.createElement('canvas');
            return !!canvas.getContext('webgl2');
        } catch (e) {
            return false;
        }
    }

    getConnectionType() {
        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        return conn ? conn.effectiveType : '4g'; // Default to 4g
    }

    shouldUse3D() {
        const caps = this.capabilities;
        
        // Don't use 3D on mobile
        if (caps.isMobile) return false;
        
        // Require WebGL
        if (!caps.webgl) return false;
        
        // Check connection (avoid 3D on slow connections)
        if (caps.connection === 'slow-2g' || caps.connection === '2g') return false;
        
        // Check device memory (require at least 4GB)
        if (caps.deviceMemory < 4) return false;
        
        return true;
    }

    get3DConfig() {
        const caps = this.capabilities;
        
        if (caps.isDesktop && caps.webgl2 && caps.connection === '4g') {
            return {
                quality: 'high',
                particleCount: 500,
                textureSize: 2048,
                shadowQuality: 'high',
                antialiasing: true,
                fps: 60
            };
        } else if (caps.isTablet || (caps.isDesktop && caps.webgl)) {
            return {
                quality: 'medium',
                particleCount: 200,
                textureSize: 1024,
                shadowQuality: 'medium',
                antialiasing: true,
                fps: 30
            };
        } else {
            return {
                quality: 'low',
                particleCount: 50,
                textureSize: 512,
                shadowQuality: 'none',
                antialiasing: false,
                fps: 24
            };
        }
    }

    getOptimalExperience() {
        if (this.shouldUse3D()) {
            return 'enhanced'; // Full 3D experience
        } else if (this.capabilities.isTablet) {
            return 'balanced'; // Basic 3D or advanced 2D
        } else {
            return 'core'; // Pure 2D, optimized for mobile
        }
    }
}

// Initialize
const deviceCaps = new DeviceCapabilities();
const EXPERIENCE_LEVEL = deviceCaps.getOptimalExperience();
const USE_3D = deviceCaps.shouldUse3D();
const CONFIG_3D = deviceCaps.get3DConfig();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.deviceCapabilities = deviceCaps;
    window.EXPERIENCE_LEVEL = EXPERIENCE_LEVEL;
    window.USE_3D = USE_3D;
    window.CONFIG_3D = CONFIG_3D;
}

console.log('🎨 Experience Level:', EXPERIENCE_LEVEL);
console.log('🎮 3D Enabled:', USE_3D);
console.log('⚙️ 3D Config:', CONFIG_3D);


