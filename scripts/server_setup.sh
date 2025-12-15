#!/bin/bash
#
# Скрипт первоначальной настройки сервера для Astavaisya
# Запускать на сервере от root или с sudo
#
# Использование:
#   curl -sSL https://raw.githubusercontent.com/Jtileyev/telegram_app/main/scripts/server_setup.sh | sudo bash
#
# Или скачать и запустить:
#   wget https://raw.githubusercontent.com/Jtileyev/telegram_app/main/scripts/server_setup.sh
#   chmod +x server_setup.sh
#   sudo ./server_setup.sh
#

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Astavaisya Server Setup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Запустите скрипт от root: sudo $0${NC}"
  exit 1
fi

# Определяем ОС
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo -e "${RED}❌ Не удалось определить ОС${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Обнаружена ОС: $OS $VERSION${NC}"

# Переменные (можно переопределить)
APP_USER="${APP_USER:-astavaisya}"
APP_DIR="${APP_DIR:-/var/www/astavaisya}"
DOMAIN="${DOMAIN:-}"  # Опционально, для nginx

# ===================
# 1. Обновление системы
# ===================
echo -e "\n${GREEN}📦 1. Обновление системы...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt update && apt upgrade -y
    apt install -y curl wget git unzip software-properties-common
elif [ "$OS" = "centos" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
    dnf update -y
    dnf install -y curl wget git unzip
fi

# ===================
# 2. Установка Python 3.11
# ===================
echo -e "\n${GREEN}🐍 2. Установка Python 3.11...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
    apt update
    apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 || true
elif [ "$OS" = "centos" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
    dnf install -y python3.11 python3.11-pip python3.11-devel
fi

python3 --version

# ===================
# 3. Установка PHP 8.1
# ===================
echo -e "\n${GREEN}🐘 3. Установка PHP 8.1...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    add-apt-repository -y ppa:ondrej/php 2>/dev/null || true
    apt update
    apt install -y php8.1-fpm php8.1-sqlite3 php8.1-mbstring php8.1-xml php8.1-curl
elif [ "$OS" = "centos" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
    dnf install -y https://rpms.remirepo.net/enterprise/remi-release-$(rpm -E %rhel).rpm || true
    dnf module enable -y php:remi-8.1
    dnf install -y php-fpm php-sqlite3 php-mbstring php-xml php-curl
fi

php --version

# ===================
# 4. Установка Nginx
# ===================
echo -e "\n${GREEN}🌐 4. Установка Nginx...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt install -y nginx
elif [ "$OS" = "centos" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
    dnf install -y nginx
fi

systemctl enable nginx
systemctl start nginx

# ===================
# 5. Создание пользователя
# ===================
echo -e "\n${GREEN}👤 5. Создание пользователя $APP_USER...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✅ Пользователь $APP_USER создан${NC}"
else
    echo -e "${YELLOW}⚠️ Пользователь $APP_USER уже существует${NC}"
fi

# ===================
# 6. Создание директории проекта
# ===================
echo -e "\n${GREEN}📁 6. Создание директории $APP_DIR...${NC}"
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# ===================
# 7. Systemd сервис для бота
# ===================
echo -e "\n${GREEN}🤖 7. Создание systemd сервиса для бота...${NC}"
cat > /etc/systemd/system/astavaisya-bot.service << EOF
[Unit]
Description=Astavaisya Telegram Bot
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR/bot
Environment=PATH=$APP_DIR/venv/bin:/usr/bin
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=append:/var/log/astavaisya/bot.log
StandardError=append:/var/log/astavaisya/error.log

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/log/astavaisya
chown -R $APP_USER:$APP_USER /var/log/astavaisya

systemctl daemon-reload
systemctl enable astavaisya-bot
echo -e "${GREEN}✅ Сервис astavaisya-bot создан${NC}"

# ===================
# 8. Nginx конфиг для админки
# ===================
echo -e "\n${GREEN}🌐 8. Настройка Nginx...${NC}"

# Определяем имя хоста
if [ -z "$DOMAIN" ]; then
    SERVER_NAME="_"  # default server
    LISTEN_CONFIG="listen 80 default_server;"
else
    SERVER_NAME="$DOMAIN"
    LISTEN_CONFIG="listen 80;"
fi

cat > /etc/nginx/sites-available/astavaisya << EOF
server {
    $LISTEN_CONFIG
    server_name $SERVER_NAME;
    
    root $APP_DIR/admin;
    index index.php index.html;
    
    # Защита от доступа к .env и .git
    location ~ /\. {
        deny all;
    }
    
    # Защита от доступа к базе данных
    location ~ \.db$ {
        deny all;
    }
    
    # Загруженные файлы
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # PHP обработка
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
    
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

# Включаем сайт
ln -sf /etc/nginx/sites-available/astavaisya /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Проверяем конфиг
nginx -t

# Перезапускаем nginx
systemctl reload nginx

echo -e "${GREEN}✅ Nginx настроен${NC}"

# ===================
# 9. Права на директории
# ===================
echo -e "\n${GREEN}🔐 9. Настройка прав...${NC}"
chown -R $APP_USER:www-data $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/uploads 2>/dev/null || true
chmod -R 775 $APP_DIR/database 2>/dev/null || true

# ===================
# Готово!
# ===================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Установка завершена!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Следующие шаги:"
echo -e "1. Склонируйте репозиторий в $APP_DIR"
echo -e "2. Создайте .env файл из .env.example"
echo -e "3. Настройте BOT_TOKEN в .env"
echo -e "4. Создайте venv и установите зависимости:"
echo -e "   ${YELLOW}cd $APP_DIR && python3 -m venv venv${NC}"
echo -e "   ${YELLOW}source venv/bin/activate && pip install -r requirements.txt${NC}"
echo -e "5. Запустите бота:"
echo -e "   ${YELLOW}sudo systemctl start astavaisya-bot${NC}"
echo ""
echo -e "Или настройте GitHub Actions для автодеплоя (см. README)"
echo ""
