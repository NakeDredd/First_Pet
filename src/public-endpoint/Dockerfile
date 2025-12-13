FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY public_endpoint.py .
CMD ["python", "public_endpoint.py"]