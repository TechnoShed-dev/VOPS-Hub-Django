#!/bin/bash

# Define paths and filenames
BACKUP_DIR="/mnt/ssd/PUBLIC/VOPS_backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILENAME="vops_data_dump_${TIMESTAMP}.json"
FULL_BACKUP_PATH="${BACKUP_DIR}/${DUMP_FILENAME}"

# Ensure the backup directory exists on the host
mkdir -p "${BACKUP_DIR}"

echo "Starting Django data dump at ${TIMESTAMP}..."

# Execute dumpdata inside the 'web' service container and redirect output to a file on the host
# Note: 'dumpdata' outputs to stdout by default, which makes redirection easy
docker compose exec -T web python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > "${FULL_BACKUP_PATH}"

# Explanation of dumpdata options:
# --natural-foreign: Use natural keys for Foreign Key relationships, making data more readable and loadable.
# --natural-primary: Use natural keys for primary keys if defined on models, improving portability.
# --indent 2: Format the JSON output with a 2-space indent for readability.
# -T: (for docker compose exec) Disables pseudo-TTY allocation. Important for cron jobs to avoid errors.

if [ $? -eq 0 ]; then
    echo "Django data dump successful! Saved to: ${FULL_BACKUP_PATH}"
else
    echo "ERROR: Django data dump failed!"
fi
