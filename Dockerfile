FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3007

COPY . .

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:3007", "--workers", "3"]
