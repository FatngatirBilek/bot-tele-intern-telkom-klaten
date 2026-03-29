FROM python:3.11-slim

# Biar log muncul real-time
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependency langsung tanpa cache biar image kecil
RUN pip install --no-cache-dir \
    python-telegram-bot \
    gspread \
    google-auth \
    python-dotenv

# Copy script bot dan file kredensial
COPY . .

# Jalanin botnya
CMD ["python", "main.py"]
