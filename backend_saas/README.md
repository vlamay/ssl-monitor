# SSL Monitor Pro SaaS - Enterprise Backend

A complete SaaS backend for SSL certificate monitoring built with FastAPI, PostgreSQL, Redis, Celery, Stripe, and Telegram notifications.

## 🚀 Features

### Core Features
- **User Management**: JWT authentication, registration, profiles
- **SSL Monitoring**: Automated certificate expiry monitoring
- **Subscriptions**: Stripe integration with multiple plans
- **Notifications**: Email, Telegram, and webhook notifications
- **Calendly Integration**: Demo call scheduling
- **Background Tasks**: Celery for SSL checks and notifications

### Technical Features
- **FastAPI**: Modern, fast async Python web framework
- **PostgreSQL**: Robust relational database with SQLAlchemy ORM
- **Redis**: Caching and Celery message broker
- **Docker**: Containerized deployment
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Pages.dev)   │◄──►│   (API)         │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Celery        │◄──►│   Redis         │
                       │   (Workers)     │    │   (Cache/Broker)│
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Telegram      │    │   Stripe        │
                       │   (Alerts)      │    │   (Billing)     │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.104+, Python 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+
- **Cache/Queue**: Redis 7+ with Celery 5.3+
- **Authentication**: JWT with bcrypt password hashing
- **Payments**: Stripe API
- **Notifications**: Telegram Bot API, SMTP
- **Scheduling**: Calendly API
- **Deployment**: Docker, Render.com
- **Monitoring**: Prometheus metrics, health checks

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)
- Stripe account
- Telegram Bot Token
- Calendly account (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd backend_saas
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# Create database
createdb sslmonitor

# Run migrations
alembic upgrade head
```

### 4. Start Services

```bash
# Development
uvicorn app.main:app --reload

# With Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# With Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info
```

### 5. Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `STRIPE_SECRET_KEY` | Stripe API secret key | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes |
| `FRONTEND_URL` | Frontend application URL | Yes |

### Plans Configuration

```python
PLANS = {
    "free": {"monitors": 5, "checks_per_day": 24, "price": 0},
    "pro": {"monitors": 50, "checks_per_day": 1440, "price": 29},
    "enterprise": {"monitors": 500, "checks_per_day": 1440, "price": 99}
}
```

## 🔐 Authentication

### JWT Tokens
- **Access Token**: 8 days expiry
- **Refresh Token**: 30 days expiry
- **Algorithm**: HS256

### Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh tokens
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update user profile

## 📈 SSL Monitoring

### Features
- Automated SSL certificate checking
- Expiry alerts (30, 7, 3, 1 days before)
- Certificate chain validation
- Performance metrics
- Uptime tracking

### Celery Tasks
- `check_ssl_certificate` - Check single domain
- `check_all_ssl_certificates` - Batch checking
- `trigger_notifications` - Send alerts

## 💳 Billing & Subscriptions

### Stripe Integration
- **Free Trial**: 7 days
- **Monthly/Yearly**: Pro and Enterprise plans
- **Webhook Handling**: Subscription updates
- **Customer Portal**: Self-service billing

### Endpoints
- `GET /api/v1/subscriptions` - List subscriptions
- `POST /api/v1/subscriptions/checkout` - Create checkout session
- `GET /api/v1/subscriptions/portal` - Customer portal link

## 📱 Notifications

### Channels
- **Email**: SMTP integration
- **Telegram**: Bot API
- **Webhook**: Custom HTTP endpoints

### Triggers
- SSL certificate expiry alerts
- Monitor status changes
- Weekly reports
- Payment notifications

## 📅 Calendly Integration

### Features
- Demo call scheduling
- Onboarding sessions
- Support calls
- Event tracking

### Endpoints
- `GET /api/v1/calendly/link` - Get booking URL
- `POST /api/v1/calendly/webhook` - Event webhooks

## 🚀 Deployment

### Render.com Deployment

1. **Connect Repository**: Link your GitHub repo
2. **Configure Services**: Use `render.yaml` configuration
3. **Set Secrets**: Add environment variables
4. **Deploy**: Automatic deployment on push

### Environment Variables for Production

```bash
# Required
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
STRIPE_SECRET_KEY=sk_live_...
TELEGRAM_BOT_TOKEN=1234567890:ABC...

# Optional
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
CALENDLY_ACCESS_TOKEN=your-token
```

## 📊 Monitoring & Health

### Health Checks
- `GET /health` - Comprehensive health check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /metrics` - Prometheus metrics

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Performance metrics

## 🔧 Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Security check
bandit -r app/
```

## 📚 API Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Add SSL Monitor

```bash
curl -X POST "http://localhost:8000/api/v1/monitors" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "port": 443,
    "check_interval": 3600,
    "alert_before_days": 30
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/api/v1/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@sslmonitor.pro

---

**SSL Monitor Pro SaaS** - Enterprise-grade SSL certificate monitoring platform 🚀
