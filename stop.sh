#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Директория проекта (автоматическое определение)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

cd "$PROJECT_DIR" || exit 1

echo -e "${RED}Остановка админки и бота...${NC}"

# Остановка PHP сервера
if [ -f .admin.pid ]; then
    PHP_PID=$(cat .admin.pid)
    if kill -0 "$PHP_PID" 2>/dev/null; then
        kill "$PHP_PID"
        echo -e "${GREEN}PHP сервер остановлен (PID: $PHP_PID)${NC}"
    else
        echo "PHP сервер уже остановлен"
    fi
    rm .admin.pid
fi

# Остановка бота
if [ -f .bot.pid ]; then
    BOT_PID=$(cat .bot.pid)
    if kill -0 "$BOT_PID" 2>/dev/null; then
        kill "$BOT_PID"
        echo -e "${GREEN}Бот остановлен (PID: $BOT_PID)${NC}"
    else
        echo "Бот уже остановлен"
    fi
    rm .bot.pid
fi

echo -e "${GREEN}Готово!${NC}"
