# Python 3.12 rasmiy obrazi asosida
FROM python:3.12-slim

# Tizim paketlarini o'rnatish (WeasyPrint uchun zarur)
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Ish papkasini belgilash
WORKDIR /app

# Avval faqat talablarni nusxalab, keyin o'rnatish (keshni tejash uchun)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Qolgan barcha loyiha fayllarini nusxalash
COPY . .

# Render $PORT muhit o'zgaruvchisini taqdim etadi
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT