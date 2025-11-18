# Deployment Guide - Telegram Apartment Rental Bot

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Application Configuration](#application-configuration)
5. [Starting the Application](#starting-the-application)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.8 or higher
- **PHP**: 7.4 or higher with SQLite extension
- **Web Server**: Apache or Nginx (for production)
- **Memory**: Minimum 512MB RAM
- **Storage**: Minimum 1GB free space

### Required Software
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv php php-sqlite3 sqlite3

# macOS (using Homebrew)
brew install python3 php sqlite3

# Verify installations
python3 --version
php --version
sqlite3 --version
```

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/Jtileyev/telegram_app.git
cd telegram_app
```

### 2. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env File
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Telegram Bot Token (get from @BotFather)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Database
DATABASE_PATH=database/rental.db

# Platform Settings
PLATFORM_FEE_PERCENT=5.0

# Admin Credentials (for first setup)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password_here

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**⚠️ SECURITY WARNING**:
- Never commit `.env` file to git
- Use strong passwords
- Change default credentials after first login

---

## Database Setup

### 1. Create Database Schema
```bash
python3 reset_database.py
```

This creates `database/rental.db` with all required tables.

### 2. Initialize with Test Data
```bash
python3 init_database.py
```

**Save the admin password shown in the output!**

Expected output:
```
=====================================
DATABASE INITIALIZATION
=====================================

📧 Admin Email: admin@example.com
🔑 Generated Password: Xy8#mK3@pL9q

⚠️  SAVE THIS PASSWORD!

✅ Database initialized successfully!
```

### 3. Verify Database
```bash
sqlite3 database/rental.db ".tables"
```

Should show 17 tables.

---

## Application Configuration

### Directory Structure
```
telegram_app/
├── bot/                    # Telegram bot code
│   ├── main.py            # Main bot logic
│   ├── config.py          # Configuration
│   ├── database.py        # Database layer
│   ├── logger.py          # Logging system
│   ├── rate_limiter.py    # Rate limiting
│   └── ...
├── admin/                  # PHP admin panel
│   ├── index.php          # Dashboard
│   ├── login.php          # Authentication
│   └── ...
├── database/
│   ├── schema.sql         # Database schema
│   └── rental.db          # SQLite database
├── uploads/                # User uploads
│   └── apartments/        # Apartment photos
├── logs/                   # Application logs (auto-created)
├── backups/                # Database backups (auto-created)
├── .env                    # Environment variables
├── start.sh                # Start script
├── stop.sh                 # Stop script
├── backup.sh               # Backup script
└── restore.sh              # Restore script
```

### File Permissions
```bash
# Make scripts executable
chmod +x start.sh stop.sh backup.sh restore.sh

# Set proper permissions
chmod 755 admin/
chmod 644 admin/*.php
chmod 777 uploads/apartments/
chmod 644 database/rental.db
```

---

## Starting the Application

### Development Mode

#### Start Everything
```bash
./start.sh
```

This starts:
- PHP admin panel on `http://localhost:8080`
- Telegram bot

#### Check Logs
```bash
# Admin panel logs
tail -f admin.log

# Bot logs
tail -f logs/bot.log

# Error logs
tail -f logs/error.log

# Audit logs
tail -f logs/audit.log
```

#### Stop Everything
```bash
./stop.sh
```

### Testing
```bash
# Run all tests
./run_all_tests.sh

# Run specific tests
cd bot
python3 tests.py
python3 test_handlers.py

cd admin
php qa_tests.php
```

---

## Production Deployment

### 1. Server Setup (Ubuntu 20.04+)

#### Install System Packages
```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    php8.1 php8.1-fpm php8.1-sqlite3 \
    nginx \
    supervisor \
    sqlite3 \
    certbot python3-certbot-nginx
```

#### Create Application User
```bash
sudo useradd -r -m -s /bin/bash telegram_bot
sudo usermod -aG www-data telegram_bot
```

#### Deploy Application
```bash
sudo mkdir -p /opt/telegram_app
sudo chown telegram_bot:telegram_bot /opt/telegram_app

# Deploy files
sudo -u telegram_bot git clone https://github.com/Jtileyev/telegram_app.git /opt/telegram_app

# Setup environment
cd /opt/telegram_app
sudo -u telegram_bot python3 -m venv venv
sudo -u telegram_bot venv/bin/pip install -r requirements.txt

# Create .env
sudo -u telegram_bot cp .env.example .env
sudo -u telegram_bot nano .env  # Edit with production settings
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/telegram_app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /opt/telegram_app;
    index index.php;

    # Admin panel
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP-FPM
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # Deny access to sensitive files
    location ~ /\.(env|git) {
        deny all;
        return 404;
    }

    location ~ /database/ {
        deny all;
        return 404;
    }

    # Uploads
    location /uploads/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/telegram_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configure SSL (Let's Encrypt)
```bash
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

### 4. Configure Supervisor (Process Manager)

Create `/etc/supervisor/conf.d/telegram_bot.conf`:
```ini
[program:telegram_bot]
directory=/opt/telegram_app
command=/opt/telegram_app/venv/bin/python3 /opt/telegram_app/bot/main.py
user=telegram_bot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/telegram_app/logs/supervisor_bot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/opt/telegram_app/venv/bin"

[program:telegram_backup]
directory=/opt/telegram_app
command=/bin/bash /opt/telegram_app/backup.sh
user=telegram_bot
autostart=false
autorestart=false
startsecs=0
```

Enable and start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start telegram_bot
sudo supervisorctl status
```

### 5. Setup Cron for Backups

Edit crontab:
```bash
sudo -u telegram_bot crontab -e
```

Add:
```cron
# Backup database daily at 3 AM
0 3 * * * /opt/telegram_app/backup.sh >> /opt/telegram_app/logs/backup.log 2>&1

# Cleanup old logs weekly
0 4 * * 0 find /opt/telegram_app/logs -name "*.log" -mtime +30 -delete
```

---

## Monitoring & Maintenance

### Logs

#### View Real-time Logs
```bash
# Bot logs
tail -f /opt/telegram_app/logs/bot.log

# Error logs
tail -f /opt/telegram_app/logs/error.log

# Audit logs (critical operations)
tail -f /opt/telegram_app/logs/audit.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### Log Rotation
Logs automatically rotate at 10MB with 5 backups kept.

### Backups

#### Manual Backup
```bash
cd /opt/telegram_app
./backup.sh
```

#### Restore from Backup
```bash
# List available backups
./restore.sh

# Restore specific backup
./restore.sh backup_20250118_153000
```

#### Backup Location
```
/opt/telegram_app/backups/
├── backup_20250118_120000/
│   ├── rental.db
│   ├── uploads.tar.gz
│   └── backup_info.txt
└── backup_20250118_153000/
    └── ...
```

### Monitoring Bot Status
```bash
# Check if bot is running
sudo supervisorctl status telegram_bot

# Restart bot
sudo supervisorctl restart telegram_bot

# View bot logs
sudo supervisorctl tail telegram_bot
```

### Database Maintenance

#### Check Database Integrity
```bash
sqlite3 /opt/telegram_app/database/rental.db "PRAGMA integrity_check;"
```

#### Optimize Database
```bash
sqlite3 /opt/telegram_app/database/rental.db "VACUUM;"
```

#### Database Size
```bash
du -h /opt/telegram_app/database/rental.db
```

---

## Troubleshooting

### Bot Not Starting

**Check logs:**
```bash
tail -n 50 /opt/telegram_app/logs/bot.log
```

**Common issues:**
1. Invalid BOT_TOKEN in .env
2. Database file permissions
3. Missing Python dependencies

**Solutions:**
```bash
# Verify bot token
grep BOT_TOKEN /opt/telegram_app/.env

# Check permissions
ls -la /opt/telegram_app/database/rental.db

# Reinstall dependencies
cd /opt/telegram_app
venv/bin/pip install -r requirements.txt --force-reinstall
```

### Admin Panel 404 or 500 Errors

**Check Nginx configuration:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

**Check PHP-FPM:**
```bash
sudo systemctl status php8.1-fpm
sudo tail -f /var/log/php8.1-fpm.log
```

### Database Locked Errors

**Cause**: Multiple processes accessing database

**Solutions:**
```bash
# Check for stale locks
lsof /opt/telegram_app/database/rental.db

# Restart everything
sudo supervisorctl restart telegram_bot
sudo systemctl restart php8.1-fpm
```

### Rate Limiting Issues

**Check rate limiter stats in logs:**
```bash
grep "Rate limit" /opt/telegram_app/logs/bot.log
```

**Adjust limits in bot/rate_limiter.py:**
```python
default_rate_limiter = RateLimiter(
    rate_limit=10,     # requests per minute
    period=60,         # seconds
    burst_limit=20     # max burst
)
```

### High Memory Usage

**Check memory:**
```bash
free -h
ps aux | grep python
```

**Solutions:**
- Restart bot: `sudo supervisorctl restart telegram_bot`
- Optimize database: `sqlite3 database/rental.db "VACUUM;"`
- Clear old logs: `find logs/ -name "*.log" -mtime +7 -delete`

---

## Security Checklist

- [ ] Change default admin password
- [ ] Use strong BOT_TOKEN
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set proper file permissions (644 for files, 755 for directories)
- [ ] Configure firewall (ufw/iptables)
- [ ] Enable fail2ban for SSH
- [ ] Regular backups (automated)
- [ ] Update dependencies regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Never commit .env to git

---

## Updates & Upgrades

### Update Application
```bash
cd /opt/telegram_app
sudo -u telegram_bot git pull
sudo -u telegram_bot venv/bin/pip install -r requirements.txt
sudo supervisorctl restart telegram_bot
```

### Update Dependencies
```bash
cd /opt/telegram_app
sudo -u telegram_bot venv/bin/pip install --upgrade -r requirements.txt
```

---

## Support

### Documentation
- Full audit: `AUDIT_REPORT.md`
- Quick reference: `QUICK_REFERENCE.md`
- Task roadmap: `tasks/README.md`

### Getting Help
- Check logs in `logs/` directory
- Review `AUDIT_REPORT.md` for known issues
- Check GitHub issues

---

**Last Updated**: November 2024
**Version**: 1.0.0
