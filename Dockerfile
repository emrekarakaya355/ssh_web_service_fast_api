# Python imajını kullan
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli dosyaları kopyala
COPY requirements.txt .
COPY app.py .

# Gerekli paketleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı 8000 portundan başlat
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
