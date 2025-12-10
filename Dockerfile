FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY database/ ./database/
COPY schemas/ ./schemas/
COPY SQL/ ./SQL/

# Copy main application file
COPY main.py .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "sleep 10 && python main.py"]