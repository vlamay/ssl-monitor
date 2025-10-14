# SSL Monitor Pro - Installation Guide

This guide will help you install and set up SSL Monitor Pro on your system.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+
- **Memory**: Minimum 2GB RAM, Recommended 4GB+ RAM
- **Storage**: Minimum 10GB free disk space
- **Network**: Internet connection for SSL certificate checking

### Software Dependencies
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7.0 or higher
- **Docker**: 20.10 or higher (optional but recommended)

### Development Tools (Optional)
- **Git**: For version control
- **Make**: For build automation
- **curl**: For API testing

## 🚀 Installation Methods

### Method 1: Docker Installation (Recommended)

The easiest way to get started with SSL Monitor Pro is using Docker.

#### Step 1: Clone the Repository
```bash
git clone https://gitlab.com/ssl-monitor-pro/ssl-monitor-pro.git
cd ssl-monitor-pro
```

#### Step 2: Configure Environment
```bash
cp env.example .env
# Edit .env file with your configuration
```

#### Step 3: Start Services
```bash
# Start all services
docker-compose up -d

# Or use the Makefile
make docker-up
```

#### Step 4: Run Migrations
```bash
# Run database migrations
docker-compose exec backend python app/migrate.py

# Or use the Makefile
make migrate
```

#### Step 5: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Method 2: Manual Installation

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    nodejs npm postgresql postgresql-contrib redis-server \
    build-essential libpq-dev curl
```

**macOS (with Homebrew):**
```bash
brew install python@3.11 node postgresql redis
```

**Windows:**
- Install Python 3.11 from [python.org](https://python.org)
- Install Node.js from [nodejs.org](https://nodejs.org)
- Install PostgreSQL from [postgresql.org](https://postgresql.org)
- Install Redis from [redis.io](https://redis.io)

#### Step 2: Set Up Database

**Start PostgreSQL:**
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql

# Windows
# Start PostgreSQL service from Services manager
```

**Create Database and User:**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE sslmonitor;
CREATE USER sslmonitor_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sslmonitor TO sslmonitor_user;
\q
```

#### Step 3: Set Up Redis

**Start Redis:**
```bash
# Ubuntu/Debian
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS
brew services start redis

# Windows
# Start Redis service from Services manager
```

#### Step 4: Install Backend Dependencies

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Install Frontend Dependencies

```bash
cd frontend-modern
npm install
```

#### Step 6: Configure Environment

```bash
cd ..
cp env.example .env
# Edit .env file with your configuration
```

#### Step 7: Run Database Migrations

```bash
cd backend
source venv/bin/activate
python app/migrate.py
```

#### Step 8: Start Services

**Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Start Frontend (in another terminal):**
```bash
cd frontend-modern
npm run dev
```

**Start Celery Worker (in another terminal):**
```bash
cd backend
source venv/bin/activate
celery -A celery_worker worker --loglevel=info
```

**Start Celery Beat (in another terminal):**
```bash
cd backend
source venv/bin/activate
celery -A celery_worker beat --loglevel=info
```

### Method 3: Development Installation

For developers who want to contribute to the project:

#### Step 1: Clone and Setup
```bash
git clone https://gitlab.com/ssl-monitor-pro/ssl-monitor-pro.git
cd ssl-monitor-pro
make setup
```

#### Step 2: Start Development Environment
```bash
make dev
```

This will start all services with hot reloading and development tools.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
```

Key configuration options:

```env
# Database
DATABASE_URL=postgresql://sslmonitor_user:password@localhost:5432/sslmonitor

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Application
DEBUG=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Telegram (for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Database Configuration

#### PostgreSQL Settings
```env
# Connection
DATABASE_URL=postgresql://username:password@host:port/database

# Pool settings
DB_POOL_SIZE=10
DB_CONNECTION_TIMEOUT=30
```

#### Redis Settings
```env
# Connection
REDIS_URL=redis://username:password@host:port/db

# Pool settings
REDIS_POOL_SIZE=10
```

### Security Configuration

#### JWT Settings
```env
JWT_SECRET_KEY=your-jwt-secret-key-min-32-characters
JWT_EXPIRE_MINUTES=10080  # 7 days
```

#### Session Settings
```env
SESSION_TIMEOUT_MINUTES=480  # 8 hours
ENABLE_CSRF_PROTECTION=true
```

### Monitoring Configuration

#### SSL Check Settings
```env
DEFAULT_ALERT_THRESHOLD_DAYS=30
SSL_CHECK_INTERVAL_MINUTES=60
MAX_DOMAINS_FREE=5
MAX_DOMAINS_PAID=100
```

#### Notification Settings
```env
EMAIL_NOTIFICATIONS_ENABLED=true
TELEGRAM_NOTIFICATIONS_ENABLED=true
SLACK_NOTIFICATIONS_ENABLED=false
```

## 🔧 Post-Installation Setup

### Step 1: Create Admin User

```bash
# Using the API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "full_name": "Admin User"
  }'
```

### Step 2: Configure Notifications

1. **Email Setup**:
   - Configure SMTP settings in `.env`
   - Test email notifications

2. **Telegram Setup**:
   - Create a bot with @BotFather
   - Get your chat ID
   - Configure in `.env`

3. **Slack Setup** (optional):
   - Create a webhook URL
   - Configure in `.env`

### Step 3: Add Your First Domain

1. Open the web interface at http://localhost:3000
2. Register or log in
3. Add your first domain to monitor
4. Configure alert settings

## 🧪 Verification

### Health Checks

**Backend Health:**
```bash
curl http://localhost:8000/health
```

**Frontend Health:**
```bash
curl http://localhost:3000
```

**Database Connection:**
```bash
curl http://localhost:8000/api/health/database
```

**Redis Connection:**
```bash
curl http://localhost:8000/api/health/redis
```

### Test SSL Monitoring

1. Add a test domain (e.g., `example.com`)
2. Wait for the first SSL check (up to 60 seconds)
3. Verify the certificate information is displayed
4. Test notification delivery

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :3000

# Kill the process
sudo kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U sslmonitor_user -d sslmonitor
```

#### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/ssl-monitor-pro
chmod +x scripts/*.sh
```

### Logs and Debugging

#### View Application Logs
```bash
# Docker
docker-compose logs -f backend frontend

# Manual installation
tail -f backend/logs/app.log
```

#### Enable Debug Mode
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Database Logs
```bash
# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Performance Issues

#### Memory Usage
```bash
# Check memory usage
free -h
docker stats
```

#### Database Performance
```bash
# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

#### Redis Performance
```bash
# Check Redis memory usage
redis-cli info memory
```

## 📚 Next Steps

### User Guide
- Read the [User Guide](user-guide.md) to learn how to use SSL Monitor Pro
- Check the [API Documentation](api.md) for integration details

### Development
- Set up your [Development Environment](development.md)
- Read the [Contributing Guide](contributing.md)

### Production Deployment
- Review the [Production Deployment Guide](deployment.md)
- Set up [Monitoring and Observability](monitoring.md)

## 🆘 Getting Help

### Support Channels
- **Documentation**: Check this documentation first
- **Issues**: Create an issue on GitLab
- **Discussions**: Use GitLab Discussions for questions
- **Email**: Contact vla.maidaniuk@gmail.com

### Community
- **GitLab Project**: [SSL Monitor Pro](https://gitlab.com/ssl-monitor-pro/ssl-monitor-pro)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Code of Conduct**: See [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)

---

**Last updated**: October 13, 2025  
**Version**: 1.0  
**Maintainer**: SSL Monitor Pro Team
