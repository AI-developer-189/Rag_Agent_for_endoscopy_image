FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTEBUF=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/

# Create necessary directories
RUN mkdir -p uploads outputs pdfs

# Expose API port
EXPOSE 8000

# Startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]