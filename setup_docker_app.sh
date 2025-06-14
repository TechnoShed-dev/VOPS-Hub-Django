#!/bin/bash

# Define your project directory and Docker Compose file
PROJECT_ROOT=$(dirname "$0")
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
EXCEL_FILE="Vessel Hazards.xlsx" # Make sure this file is in your project root

echo "--------------------------------------------------"
echo "   VOPS-Hub Docker Setup and Initialization Script"
echo "--------------------------------------------------"
echo "Running from: $(pwd)"
echo "Using Docker Compose file: $COMPOSE_FILE"
echo "--------------------------------------------------"

# Optional: Prompt to remove database volume for a clean start
read -p "Do you want to remove the existing Docker database volume (dev_db_data) for a clean start? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing existing database volume..."
    docker volume rm dev_db_data > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Database volume 'dev_db_data' removed successfully."
    else
        echo "Warning: Could not remove 'dev_db_data' volume (it might not exist or be in use)."
    fi
fi

# 1. Stop and remove existing containers (if any)
echo "Stopping and removing existing Docker containers..."
docker compose -f "$COMPOSE_FILE" down
if [ $? -eq 0 ]; then
    echo "Existing containers stopped and removed."
else
    echo "Warning: No running containers to stop or an error occurred during shutdown. Continuing..."
fi

# 2. Build the Docker image
echo "Building Docker image..."
docker compose -f "$COMPOSE_FILE" build --no-cache # Added --no-cache
if [ $? -ne 0 ]; then
    echo "Error: Docker image build failed. Exiting."
    exit 1
fi
echo "Docker image built successfully."

# 3. Start containers in detached mode
echo "Starting Docker containers in detached mode..."
docker compose -f "$COMPOSE_FILE" up -d
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker containers. Exiting."
    exit 1
fi
echo "Docker containers started. Waiting for services to become ready..."

# Give services a moment to start up
sleep 10

# 4. Run Django database migrations
echo "Running Django database migrations for core_app..."
docker compose -f "$COMPOSE_FILE" exec web python manage.py makemigrations core_app
if [ $? -ne 0 ]; then
    echo "Error: makemigrations failed. Exiting."
    exit 1
fi

docker compose -f "$COMPOSE_FILE" exec web python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: migrate failed. Exiting."
    exit 1
fi
echo "Migrations applied."

# 5. Create Django superuser (interactive)
echo "Creating Django superuser (you will be prompted for details)..."
docker compose -f "$COMPOSE_FILE" exec web python manage.py createsuperuser
if [ $? -ne 0 ]; then
    echo "Warning: createsuperuser might have failed or been skipped. Please check manually if needed."
fi

# 6. Import data from Excel
echo "Importing data from '$EXCEL_FILE'..."
docker compose -f "$COMPOSE_FILE" exec web python import_data.py "$EXCEL_FILE"
if [ $? -ne 0 ]; then
    echo "Warning: Data import might have failed or been skipped. Please check manually if needed."
fi
echo "Data import process initiated."

echo "--------------------------------------------------"
echo "Docker setup and initialization complete!"
echo "Your Django app should be running at http://localhost:8000 (or your Pi's IP/domain)"
echo "--------------------------------------------------"

exit 0
