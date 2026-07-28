FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml .

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["python", "test1.py"]
