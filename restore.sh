#!/bin/bash

# Database restore script
# Restores database and uploads from a backup

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Paths
BACKUP_DIR="$PROJECT_DIR/backups"
DB_PATH="$PROJECT_DIR/database/rental.db"
UPLOADS_DIR="$PROJECT_DIR/uploads"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}DATABASE RESTORE SCRIPT${NC}"
echo -e "${BLUE}================================${NC}"

# Check if backup name provided
if [ -z "$1" ]; then
    echo -e "${RED}✗ No backup name provided${NC}"
    echo -e "\nUsage: ./restore.sh <backup_name>"
    echo -e "\nAvailable backups:"

    if [ -d "$BACKUP_DIR" ]; then
        BACKUPS=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" | sort -r)
        if [ -n "$BACKUPS" ]; then
            echo "$BACKUPS" | while read -r backup; do
                BACKUP_NAME=$(basename "$backup")
                BACKUP_DATE=$(echo "$BACKUP_NAME" | sed 's/backup_//' | sed 's/_/ /')
                BACKUP_SIZE=$(du -sh "$backup" | cut -f1)
                echo -e "  • ${GREEN}$BACKUP_NAME${NC} (${BACKUP_SIZE}) - $BACKUP_DATE"
            done
        else
            echo -e "${YELLOW}  No backups found${NC}"
        fi
    else
        echo -e "${YELLOW}  Backup directory not found${NC}"
    fi
    exit 1
fi

BACKUP_NAME="$1"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Check if backup exists
if [ ! -d "$BACKUP_PATH" ]; then
    echo -e "${RED}✗ Backup not found: $BACKUP_NAME${NC}"
    exit 1
fi

# Check if database backup exists
if [ ! -f "$BACKUP_PATH/rental.db" ]; then
    echo -e "${RED}✗ Database file not found in backup${NC}"
    exit 1
fi

echo -e "\n${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
echo -e "Backup: $BACKUP_NAME"

# Show backup info if available
if [ -f "$BACKUP_PATH/backup_info.txt" ]; then
    echo -e "\n${BLUE}Backup information:${NC}"
    cat "$BACKUP_PATH/backup_info.txt" | grep -E "Date:|Database Size:|Uploads:"
fi

# Confirm restore
read -p $'\nAre you sure you want to restore? (yes/no): ' CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Starting restore...${NC}"

# Create safety backup of current database
if [ -f "$DB_PATH" ]; then
    echo -e "\n${BLUE}1. Creating safety backup of current database...${NC}"
    SAFETY_BACKUP="$BACKUP_DIR/safety_backup_$(date +"%Y%m%d_%H%M%S")"
    mkdir -p "$SAFETY_BACKUP"
    cp "$DB_PATH" "$SAFETY_BACKUP/rental.db"
    echo -e "${GREEN}✓ Safety backup created: $(basename "$SAFETY_BACKUP")${NC}"
fi

# Restore database
echo -e "\n${BLUE}2. Restoring database...${NC}"
if cp "$BACKUP_PATH/rental.db" "$DB_PATH"; then
    echo -e "${GREEN}✓ Database restored${NC}"
else
    echo -e "${RED}✗ Failed to restore database${NC}"
    exit 1
fi

# Restore uploads if available
if [ -f "$BACKUP_PATH/uploads.tar.gz" ]; then
    echo -e "\n${BLUE}3. Restoring uploads...${NC}"

    # Backup current uploads
    if [ -d "$UPLOADS_DIR" ]; then
        echo -e "  Creating backup of current uploads..."
        tar -czf "$SAFETY_BACKUP/uploads.tar.gz" -C "$PROJECT_DIR" uploads 2>/dev/null
    fi

    # Remove current uploads
    if [ -d "$UPLOADS_DIR" ]; then
        rm -rf "$UPLOADS_DIR"
    fi

    # Extract backup
    if tar -xzf "$BACKUP_PATH/uploads.tar.gz" -C "$PROJECT_DIR"; then
        echo -e "${GREEN}✓ Uploads restored${NC}"
    else
        echo -e "${RED}✗ Failed to restore uploads${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠ No uploads backup found${NC}"
fi

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✅ RESTORE COMPLETED SUCCESSFULLY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "\n📋 Restored:"
echo -e "  • Database: $DB_PATH"
if [ -f "$BACKUP_PATH/uploads.tar.gz" ]; then
    echo -e "  • Uploads: $UPLOADS_DIR"
fi

echo -e "\n💡 Safety backup created at:"
echo -e "   $SAFETY_BACKUP"
echo -e "   (In case you need to revert)"

echo -e "\n🔄 You may need to restart the application:"
echo -e "   ./stop.sh && ./start.sh"

exit 0
