FROM python:3.11-slim

WORKDIR /app

# Install system deps for python-docx
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Expose
EXPOSE 8000

# Run
CMD ["uvicorn", "assessment_engine.api:app", "--host", "0.0.0.0", "--port", "8000"]
