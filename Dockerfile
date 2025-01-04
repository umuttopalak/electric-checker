FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3003

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3003", "--access-logfile", "-", "wsgi:app"]
