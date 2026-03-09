FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/GrungaBackend

CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
