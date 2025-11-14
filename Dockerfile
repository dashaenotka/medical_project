FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "medical_project.wsgi:application"]