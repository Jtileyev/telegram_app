#!/bin/bash

# Database backup script
# Creates timestamped backups of the SQLite database and uploads directory

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Backup configuration
BACKUP_DIR="$PROJECT_DIR/backups"
DB_PATH="$PROJECT_DIR/database/rental.db"
UPLOADS_DIR="$PROJECT_DIR/uploads"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="backup_${TIMESTAMP}"

# Retention policy (days)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}DATABASE BACKUP SCRIPT${NC}"
echo -e "${BLUE}================================${NC}"

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    echo -e "${GREEN}✓ Created backup directory${NC}"
fi

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}✗ Database not found at: $DB_PATH${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Starting backup...${NC}"
echo -e "Timestamp: $(date)"
echo -e "Backup name: $BACKUP_NAME"

# Create backup subdirectory
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

# 1. Backup database
echo -e "\n${BLUE}1. Backing up database...${NC}"
if cp "$DB_PATH" "$BACKUP_PATH/rental.db"; then
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "${GREEN}✓ Database backed up (${DB_SIZE})${NC}"
else
    echo -e "${RED}✗ Failed to backup database${NC}"
    exit 1
fi

# 2. Backup uploads directory
echo -e "\n${BLUE}2. Backing up uploads...${NC}"
if [ -d "$UPLOADS_DIR" ]; then
    if tar -czf "$BACKUP_PATH/uploads.tar.gz" -C "$PROJECT_DIR" uploads 2>/dev/null; then
        UPLOADS_SIZE=$(du -h "$BACKUP_PATH/uploads.tar.gz" | cut -f1)
        echo -e "${GREEN}✓ Uploads backed up (${UPLOADS_SIZE})${NC}"
    else
        echo -e "${YELLOW}⚠ Failed to backup uploads (directory might be empty)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Uploads directory not found${NC}"
fi

# 3. Create backup metadata
echo -e "\n${BLUE}3. Creating backup metadata...${NC}"
cat > "$BACKUP_PATH/backup_info.txt" << EOF
Backup Information
==================
Date: $(date)
Timestamp: $TIMESTAMP
Database: $(basename "$DB_PATH")
Database Size: $(stat -f%z "$DB_PATH" 2>/dev/null || stat -c%s "$DB_PATH" 2>/dev/null) bytes
Uploads: $([ -d "$UPLOADS_DIR" ] && echo "Included" || echo "Not found")
Backup Location: $BACKUP_PATH
EOF
echo -e "${GREEN}✓ Metadata created${NC}"

# 4. Calculate total backup size
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

# 5. Clean up old backups (retention policy)
echo -e "\n${BLUE}4. Cleaning up old backups...${NC}"
if [ "$RETENTION_DAYS" -gt 0 ]; then
    OLD_BACKUPS=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" -mtime +$RETENTION_DAYS)
    if [ -n "$OLD_BACKUPS" ]; then
        echo "$OLD_BACKUPS" | while read -r old_backup; do
            rm -rf "$old_backup"
            echo -e "${YELLOW}  Removed: $(basename "$old_backup")${NC}"
        done
    else
        echo -e "${GREEN}  No old backups to remove${NC}"
    fi
else
    echo -e "${YELLOW}  Retention policy disabled (keeping all backups)${NC}"
fi

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✅ BACKUP COMPLETED SUCCESSFULLY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "\n📦 Backup Summary:"
echo -e "  Location: $BACKUP_PATH"
echo -e "  Total size: $BACKUP_SIZE"
echo -e "  Retention: ${RETENTION_DAYS} days"
echo -e "\n📋 Backup contains:"
echo -e "  • rental.db (database)"
if [ -f "$BACKUP_PATH/uploads.tar.gz" ]; then
    echo -e "  • uploads.tar.gz (apartment photos)"
fi
echo -e "  • backup_info.txt (metadata)"

echo -e "\n💡 To restore from this backup, run:"
echo -e "   ./restore.sh $BACKUP_NAME"

# Count total backups
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" | wc -l)
echo -e "\n📊 Total backups: $TOTAL_BACKUPS"

exit 0
