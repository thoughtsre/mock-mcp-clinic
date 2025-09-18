FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime deps first for better caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "server.py"]


