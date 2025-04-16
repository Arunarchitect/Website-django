# Use official Python image
FROM python:3.10-slim

# Accept SECRET_KEY as a build-time argument
ARG SECRET_KEY

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY=${SECRET_KEY}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port (optional, for debugging or if not using a socket)
EXPOSE 8000

# Start Gunicorn via Unix socket
CMD ["gunicorn", "webdjango.wsgi:application", "--bind", "unix:/app/gunicorn.sock"]
