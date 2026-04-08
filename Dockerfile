FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (cached layer unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/
COPY server/ ./server/
COPY inference.py .
COPY openenv.yaml .

EXPOSE 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
