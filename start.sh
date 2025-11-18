#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Директория проекта
PROJECT_DIR="/home/jaras/vscode_projects/telegram_app"

cd "$PROJECT_DIR" || exit 1

echo -e "${BLUE}Запуск админки и бота...${NC}"

# Запуск PHP админки в фоне
echo -e "${GREEN}Запуск PHP админки на localhost:8080...${NC}"
php -S localhost:8080 -t . > admin.log 2>&1 &
PHP_PID=$!
echo "PHP сервер запущен (PID: $PHP_PID)"

# Небольшая задержка
sleep 1

# Запуск Python бота
echo -e "${GREEN}Запуск Telegram бота...${NC}"
venv/bin/python3 bot/main.py > bot.log 2>&1 &
BOT_PID=$!
echo "Бот запущен (PID: $BOT_PID)"

# Сохранение PID в файл для возможности остановки
echo "$PHP_PID" > .admin.pid
echo "$BOT_PID" > .bot.pid

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Админка: http://localhost:8080${NC}"
echo -e "${GREEN}Логи админки: admin.log${NC}"
echo -e "${GREEN}Логи бота: bot.log${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Для остановки используйте: ./stop.sh"
echo -e "Для просмотра логов: tail -f admin.log или tail -f bot.log"
