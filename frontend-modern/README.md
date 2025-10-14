# 🎨 SSL Monitor Pro - Modern Frontend

Modern, responsive frontend for SSL Monitor Pro built with vanilla JavaScript, Tailwind CSS, and Alpine.js.

## 📁 Structure

```
frontend-modern/
├── index.html          # Landing page
├── dashboard.html      # Dashboard with real-time monitoring
├── css/
│   └── style.css      # Custom styles
└── js/
    └── app.js         # API client and utilities
```

## ✨ Features

### Landing Page (`index.html`)
- ✅ Hero section with compelling value proposition
- ✅ Features showcase (6 key features)
- ✅ Pricing table (Starter €19, Professional €49, Enterprise €149)
- ✅ CTA sections
- ✅ Responsive design
- ✅ Smooth animations

### Dashboard (`dashboard.html`)
- ✅ Real-time domain monitoring
- ✅ Add/delete domains
- ✅ SSL certificate status checks
- ✅ Statistics cards
- ✅ Auto-refresh every 30 seconds
- ✅ Visual status indicators (✅ ⚠️ 🚨 ❌)
- ✅ API integration

### JavaScript API Client (`js/app.js`)
- ✅ Complete REST API wrapper
- ✅ Error handling
- ✅ Utility functions
- ✅ Notification system

## 🚀 Quick Start

### Local Development

**Option 1: Python Simple Server**
```bash
cd frontend-modern
python3 -m http.server 8080
# Open http://localhost:8080
```

**Option 2: Node.js serve**
```bash
npx serve frontend-modern
```

**Option 3: PHP Built-in Server**
```bash
cd frontend-modern
php -S localhost:8080
```

### Testing with Local Backend

1. Start backend API:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. Open dashboard:
```
http://localhost:8080/dashboard.html
```

The app will automatically detect localhost and use `http://localhost:8000` as API base.

### Testing with Production API

Just open the dashboard - it will automatically use:
```
https://ssl-monitor-api.onrender.com
```

## 🎯 API Configuration

Edit `js/app.js` to change API endpoint:

```javascript
const API_BASE = 'https://your-api-url.com';
```

Or use environment detection (default):
```javascript
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://ssl-monitor-api.onrender.com';
```

## 📦 Dependencies

All dependencies are loaded via CDN:
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Google Fonts** - Inter font family

No build process required! 🎉

## 🌐 Deployment Options

### Option 1: Cloudflare Pages (Recommended)

1. Push code to GitHub
2. Go to Cloudflare Dashboard → Pages
3. Create project → Connect GitHub
4. Build settings:
   - Build command: (none)
   - Build output directory: `frontend-modern`
5. Deploy!

### Option 2: Render Static Site

Add to `render.yaml`:
```yaml
- type: static
  name: ssl-monitor-frontend
  buildCommand: echo "Static files"
  staticPublishPath: frontend-modern
  routes:
    - type: rewrite
      source: /*
      destination: /index.html
```

### Option 3: Netlify

```bash
netlify deploy --dir=frontend-modern --prod
```

### Option 4: Vercel

```bash
vercel --prod frontend-modern
```

### Option 5: GitHub Pages

```bash
# In repository settings:
# Pages → Source → Deploy from branch
# Branch: main, Folder: /frontend-modern
```

## 🎨 Customization

### Colors

Edit `index.html` and `dashboard.html` to change color scheme:
```html
<!-- Purple accent (default) -->
class="bg-purple-600"

<!-- Change to blue -->
class="bg-blue-600"

<!-- Change to green -->
class="bg-green-600"
```

### Branding

1. **Logo**: Replace 🔒 emoji with your logo image
2. **Company Name**: Search and replace "SSL Monitor Pro"
3. **Contact Info**: Update footer with your details

### Pricing

Edit pricing cards in `index.html`:
```html
<div class="text-5xl font-bold text-gray-900">€49</div>
```

## 📱 Mobile Responsive

✅ All pages are fully responsive:
- Desktop: Full layout with all features
- Tablet: Adapted grid layouts
- Mobile: Stacked layout with mobile menu

## 🔧 API Methods

Available in `js/app.js`:

```javascript
// Health
api.healthCheck()

// Domains
api.getDomains()
api.getDomain(id)
api.addDomain(name)
api.updateDomain(id, updates)
api.deleteDomain(id)

// SSL Checks
api.checkSSL(id)
api.getSSLStatus(id)
api.getSSLHistory(id, limit)

// Statistics
api.getStatistics()

// Billing
api.getBillingPlans()
```

## 🐛 Troubleshooting

### CORS Errors

If you get CORS errors, ensure your backend has CORS enabled:

```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Failed

Check:
1. Backend is running
2. API_BASE URL is correct in `js/app.js`
3. Network tab in browser DevTools for errors

### Domains Not Loading

1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API responses in Network tab

## 📊 Features Roadmap

### Phase 1: Core (Completed ✅)
- [x] Landing page
- [x] Dashboard
- [x] Domain management
- [x] SSL checks
- [x] Real-time updates

### Phase 2: Authentication (Future)
- [ ] User login/registration
- [ ] Protected routes
- [ ] Session management
- [ ] Multi-user support

### Phase 3: Advanced Features (Future)
- [ ] WebSocket real-time updates
- [ ] Advanced filtering and search
- [ ] SSL history charts
- [ ] Export reports (PDF/CSV)
- [ ] Email notification settings
- [ ] Telegram bot integration UI

## 💡 Tips

1. **Auto-refresh**: Dashboard refreshes every 30 seconds automatically
2. **Status Colors**: 
   - Green (✅) = Healthy (>30 days)
   - Yellow (⚠️) = Warning (0-30 days)
   - Red (🚨) = Critical (expired)
   - Gray (❌) = Error
3. **Notifications**: Appear top-right, auto-dismiss after 3 seconds

## 📞 Support

**Email**: vla.maidaniuk@gmail.com  
**Phone**: +420 721 579 603  
**GitHub**: https://192.168.1.10/root/ssl-monitor-pro

## 🎉 Ready to Deploy!

Your modern SSL Monitor Pro frontend is complete and ready for production deployment!

**What's included:**
- ✅ Beautiful landing page
- ✅ Functional dashboard
- ✅ Complete API integration
- ✅ Real-time monitoring
- ✅ Mobile responsive
- ✅ No build process required

Just deploy to your favorite static hosting and you're live! 🚀


