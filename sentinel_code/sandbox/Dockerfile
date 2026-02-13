FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY vulnerable_code.py .

EXPOSE 5000

CMD ["python", "app.py"]
