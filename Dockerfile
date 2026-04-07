FROM python:3.12-slim

WORKDIR /app

# Install deps first (cached layer unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/
COPY inference.py .
COPY openenv.yaml .

CMD ["python", "inference.py"]
