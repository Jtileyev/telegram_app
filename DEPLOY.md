# Развёртывание Astavaisya на новом сервере

## Требования

- Ubuntu 22.04+ (или Debian 12+)
- Root-доступ или sudo
- Домен (опционально, для HTTPS)

## 1. Автоматическая установка зависимостей

Скрипт установит Python 3.11, PHP 8.1, Nginx, создаст пользователя и systemd-сервис:

```bash
# Если есть домен — задать переменную перед запуском:
# export DOMAIN=actavaysa.kz

sudo bash scripts/server_setup.sh
```

Или вручную:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl nginx python3.11 python3.11-venv python3.11-dev \
    php8.1-fpm php8.1-sqlite3 php8.1-mbstring php8.1-xml php8.1-curl
```

## 2. Клонирование проекта

```bash
cd /var/www
git clone https://github.com/Jtileyev/telegram_app.git astavaisya
cd astavaisya
```

## 3. Python окружение

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Конфигурация

```bash
cp .env.example .env
nano .env
```

Обязательно заполнить:

| Параметр | Описание |
|----------|----------|
| `BOT_TOKEN` | Токен от @BotFather |
| `ADMIN_EMAIL` | Email для входа в админку |
| `ADMIN_PASSWORD` | Пароль для входа в админку |
| `ENVIRONMENT` | `production` |

## 5. Инициализация базы данных

```bash
python database/init_database.py
```

## 6. Права и директории

```bash
# Создать папку для загрузок
mkdir -p uploads/apartments

# Симлинк для картинок в админке
ln -sf ../uploads admin/uploads

# Создать папку логов
mkdir -p logs /var/log/astavaisya

# Права (www-data — пользователь nginx/php-fpm)
sudo chown -R www-data:www-data /var/www/astavaisya
sudo chmod -R 755 /var/www/astavaisya
sudo chmod -R 775 uploads/ database/
```

## 7. Настройка Nginx

```bash
sudo cp nginx/astavaisya.conf /etc/nginx/sites-available/astavaisya
sudo ln -sf /etc/nginx/sites-available/astavaisya /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

Если нужно — отредактировать `server_name` в конфиге:

```bash
sudo nano /etc/nginx/sites-available/astavaisya
```

Проверить и перезапустить:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Запуск бота как systemd-сервиса

Сервис создаётся автоматически скриптом `server_setup.sh`. Если делали вручную:

```bash
sudo cat > /etc/systemd/system/astavaisya-bot.service << 'EOF'
[Unit]
Description=Astavaisya Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/astavaisya/bot
Environment=PATH=/var/www/astavaisya/venv/bin:/usr/bin
ExecStart=/var/www/astavaisya/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/astavaisya/bot.log
StandardError=append:/var/log/astavaisya/error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable astavaisya-bot
sudo systemctl start astavaisya-bot
```

## 9. Проверка

```bash
# Статус бота
sudo systemctl status astavaisya-bot

# Логи бота
sudo tail -f /var/log/astavaisya/bot.log

# Статус nginx
sudo systemctl status nginx

# Проверить админку
curl -I http://localhost/login.php
```

## 10. HTTPS (опционально, рекомендуется)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d actavaysa.kz -d www.actavaysa.kz
```

Certbot автоматически обновит nginx-конфиг и настроит автопродление.

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Перезапуск бота | `sudo systemctl restart astavaisya-bot` |
| Логи бота | `sudo journalctl -u astavaisya-bot -f` |
| Перезапуск nginx | `sudo systemctl reload nginx` |
| Бэкап БД | `./scripts/backup.sh` |
| Восстановление | `./scripts/restore.sh backup_YYYYMMDD_HHMMSS` |

## Миграция данных со старого сервера

Если нужно перенести данные:

```bash
# На старом сервере
./scripts/backup.sh
# Скопировать папку backups/backup_XXXXXXXX_XXXXXX/ на новый сервер

# На новом сервере
cp backup_*/rental.db database/rental.db
tar -xzf backup_*/uploads.tar.gz -C .
sudo chown -R www-data:www-data database/ uploads/
sudo systemctl restart astavaisya-bot
```
