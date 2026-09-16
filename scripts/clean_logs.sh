#!/bin/bash
LOG_DIR="/tmp/backups_isocoul"

if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -type f -name "*.sql" -mtime +7 -exec rm -f {} \;
    echo "Nettoyage des sauvegardes obsolètes effectué."
    exit 0
else
    echo "Répertoire de logs introuvable."
    exit 1
fi
