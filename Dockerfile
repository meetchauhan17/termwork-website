# Use an official lightweight Python image.
FROM python:3.10-slim

# Install system dependencies, including LibreOffice for PDF conversion
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    ure \
    libreoffice-java-common \
    libreoffice-core \
    libreoffice-common \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure outputs and temp directories exist
RUN mkdir -p outputs temp

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "app:app"]
