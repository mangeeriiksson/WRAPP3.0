# Använd en stabil Python-bild
FROM python:3.9-slim

# Installera nödvändiga systemberoenden
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Sätt arbetskatalogen
WORKDIR /app

# Kopiera och installera beroenden
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Kopiera hela projektet
COPY . .

# Starta applikationen
CMD ["python", "app.py"]
