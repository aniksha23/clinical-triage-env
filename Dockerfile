FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (cached layer unless requirements.txt changes)
COPY requirements-inference.txt .
RUN pip install --no-cache-dir -r requirements-inference.txt

# Copy app code
COPY app/ ./app/
COPY inference.py .
COPY main.py .
COPY openenv.yaml .

EXPOSE 7860
CMD ["python", "main.py"]
