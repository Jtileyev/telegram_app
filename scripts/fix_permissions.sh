#!/bin/bash

# ============================================
# Fix Permissions Script for Astavaisya
# ============================================
# Скрипт для установки правильных прав доступа
# на файлы и папки проекта
# ============================================

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Путь к проекту (измените при необходимости)
PROJECT_PATH="/var/www/astavaisya"

# Пользователь веб-сервера (обычно www-data для Apache/Nginx)
WEB_USER="www-data"
WEB_GROUP="www-data"

# Проверка запуска от root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Ошибка: Этот скрипт нужно запускать от root (sudo)${NC}"
   echo "Использование: sudo $0"
   exit 1
fi

# Проверка существования директории проекта
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Ошибка: Директория $PROJECT_PATH не найдена${NC}"
    echo "Укажите правильный путь к проекту в переменной PROJECT_PATH"
    exit 1
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Исправление прав доступа для Astavaisya  ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Путь к проекту: ${YELLOW}$PROJECT_PATH${NC}"
echo -e "Пользователь веб-сервера: ${YELLOW}$WEB_USER:$WEB_GROUP${NC}"
echo ""

# 1. Создание необходимых директорий
echo -e "${YELLOW}[1/5]${NC} Создание директорий..."

mkdir -p "$PROJECT_PATH/uploads/apartments"
mkdir -p "$PROJECT_PATH/logs"
mkdir -p "$PROJECT_PATH/database"

echo -e "  ✓ uploads/apartments"
echo -e "  ✓ logs"
echo -e "  ✓ database"

# Директории, которые НЕ нужно трогать (содержат бинарники с особыми правами)
EXCLUDE_DIRS="-path $PROJECT_PATH/venv -prune -o -path $PROJECT_PATH/.git -prune -o -path $PROJECT_PATH/node_modules -prune -o"

# 2. Установка владельца для всего проекта (кроме venv)
echo -e "${YELLOW}[2/6]${NC} Установка владельца файлов..."

# Устанавливаем владельца только для нужных директорий
for dir in admin bot database logs uploads scripts tasks; do
    if [ -d "$PROJECT_PATH/$dir" ]; then
        chown -R $WEB_USER:$WEB_GROUP "$PROJECT_PATH/$dir"
    fi
done
chown $WEB_USER:$WEB_GROUP "$PROJECT_PATH"/*.sh 2>/dev/null
chown $WEB_USER:$WEB_GROUP "$PROJECT_PATH"/*.py 2>/dev/null
chown $WEB_USER:$WEB_GROUP "$PROJECT_PATH"/*.txt 2>/dev/null
chown $WEB_USER:$WEB_GROUP "$PROJECT_PATH"/*.md 2>/dev/null
echo -e "  ✓ Владелец установлен (venv, .git исключены)"

# 3. Установка прав на директории (755 - rwxr-xr-x)
echo -e "${YELLOW}[3/6]${NC} Установка прав на директории (755)..."

find "$PROJECT_PATH" $EXCLUDE_DIRS -type d -exec chmod 755 {} \;
echo -e "  ✓ Все директории: 755 (venv, .git исключены)"

# 4. Установка прав на файлы (644 - rw-r--r--)
echo -e "${YELLOW}[4/6]${NC} Установка прав на файлы (644)..."

find "$PROJECT_PATH" $EXCLUDE_DIRS -type f -exec chmod 644 {} \;
echo -e "  ✓ Все файлы: 644 (venv, .git исключены)"

# 5. Установка прав на записываемые директории (775)
echo -e "${YELLOW}[5/6]${NC} Установка прав на записываемые директории..."

# Uploads - для загрузки файлов
chmod 775 "$PROJECT_PATH/uploads"
chmod 775 "$PROJECT_PATH/uploads/apartments"

# Logs - для записи логов
chmod 775 "$PROJECT_PATH/logs"

# Database - для записи SQLite
chmod 775 "$PROJECT_PATH/database"

# Права на файл базы данных (если существует)
if [ -f "$PROJECT_PATH/database/rental.db" ]; then
    chmod 664 "$PROJECT_PATH/database/rental.db"
    echo -e "  ✓ database/rental.db: 664"
fi

# Права на исполняемые скрипты в корне проекта
chmod +x "$PROJECT_PATH"/*.sh 2>/dev/null
echo -e "  ✓ *.sh (корень): исполняемые"

# Права на исполняемые скрипты в папке scripts
if [ -d "$PROJECT_PATH/scripts" ]; then
    chmod +x "$PROJECT_PATH/scripts"/*.sh 2>/dev/null
    echo -e "  ✓ scripts/*.sh: исполняемые"
fi

echo -e "  ✓ uploads/: 775"
echo -e "  ✓ uploads/apartments/: 775"
echo -e "  ✓ logs/: 775"
echo -e "  ✓ database/: 775"

# 6. Проверка и восстановление venv (если сломано)
echo -e "${YELLOW}[6/6]${NC} Проверка виртуального окружения..."

if [ -d "$PROJECT_PATH/venv" ]; then
    # Восстановить права на бинарники venv
    chmod +x "$PROJECT_PATH/venv/bin/"* 2>/dev/null
    echo -e "  ✓ venv/bin/*: исполняемые"
else
    echo -e "  ⚠ venv не найден (пропущено)"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Права доступа успешно настроены!         ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Вывод итоговой информации
echo -e "Проверка прав на ключевые директории:"
echo ""
ls -la "$PROJECT_PATH" | grep -E "uploads|logs|database|venv"
echo ""
ls -la "$PROJECT_PATH/uploads/"
