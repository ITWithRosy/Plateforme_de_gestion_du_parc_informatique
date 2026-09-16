#!/bin/bash

BACKUP_DIR="/tmp/backups_isocoul"
DATE=$(date +'%Y-%m-%d_%H-%M-%S')
PG_HOST="192.168.10.5"
PG_PORT="5432"
PG_USER="adminsysteme"
PG_DB="plateforme_db"
export PGPASSWORD="UNDERCOVER"

mkdir -p "$BACKUP_DIR"
pg_dump -h $PG_HOST -p $PG_PORT -U $PG_USER $PG_DB > "$BACKUP_DIR/plateforme_db_$DATE.sql" 2>&1
if [ $? -eq 0 ]; then
    echo "Sauvegarde réussie : $BACKUP_DIR/plateforme_db_$DATE.sql"
    exit 0
else
    echo "Échec de la sauvegarde"
    exit 1
fi