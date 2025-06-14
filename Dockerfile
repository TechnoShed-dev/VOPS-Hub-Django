# Use an official Python runtime as a parent image
FROM python:3.13-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    # Add other system deps if your Python packages require them (e.g., libjpeg-dev for Pillow)
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the working directory
# In development, this will be overridden by the volume mount, but it's good for building.
COPY . .

# Expose the port your Django app will run on (default 8000)
EXPOSE 8000

# Command to run the application (will be overridden by docker-compose in dev)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]