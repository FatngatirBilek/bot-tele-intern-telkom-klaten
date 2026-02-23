# Bot Telegram Intern Telkom Klaten

Bot Telegram untuk mengelola data Google Spreadsheet terkait pencatatan tiket gangguan internet di Telkom Klaten.

## Fitur

- `/start` — Salam pembuka dari bot
- `/hai` — Sapaan personal
- `/format` — Menampilkan format perintah
- `/edit <NO> <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>` — Edit baris di spreadsheet
- `/input <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>` — Tambah data baru ke spreadsheet

## Setup Lokal

1. **Clone repository:**
   ```bash
   git clone https://github.com/FatngatirBilek/bot-tele-intern-telkom-klaten.git
   cd bot-tele-intern-telkom-klaten
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi:**
   - Salin `.env.example` ke `.env` dan isi nilai-nilainya:
     ```bash
     cp .env.example .env
     ```
   - Letakkan file JSON service account Google di root project (misalnya `tele-bot-inter-8af7bdb6401f.json`), **atau** isi variabel `GOOGLE_CREDENTIALS_JSON` di `.env` dengan isi JSON tersebut.

4. **Jalankan bot:**
   ```bash
   python bot.py
   ```

## Hosting 24/7 di GitHub Actions

Kamu bisa menjalankan bot ini 24/7 menggunakan GitHub Actions tanpa server tambahan:

1. **Buka repository di GitHub → Settings → Secrets and variables → Actions.**

2. **Tambahkan repository secrets berikut:**

   | Secret Name              | Nilai                                              |
   | ------------------------ | -------------------------------------------------- |
   | `TELEGRAM_TOKEN`         | Token bot dari @BotFather                          |
   | `SPREADSHEET_ID`         | ID spreadsheet (dari URL spreadsheet)              |
   | `SHEET_GID`              | GID sheet/tab (default: `0`)                       |
   | `GOOGLE_CREDENTIALS_JSON`| Isi lengkap file JSON service account Google       |

3. **Aktifkan workflow:**
   - Buka tab **Actions** di repository.
   - Pilih workflow **Run Telegram Bot**.
   - Klik **Run workflow** untuk memulai.

   Bot akan otomatis restart setiap 5 jam melalui scheduled workflow.

> **Catatan:** GitHub Actions memiliki batas waktu maksimal 6 jam per job. Workflow ini menggunakan timeout ~5 jam dengan restart otomatis setiap 5 jam. Akun GitHub gratis memiliki kuota bulanan untuk Actions minutes — pantau penggunaan di **Settings → Billing**.

## Hosting dengan Docker

```bash
docker build -t bot-telkom .
docker run -d --env-file .env bot-telkom
```

## Konfigurasi

| Variabel                  | Deskripsi                                           |
| ------------------------- | --------------------------------------------------- |
| `TELEGRAM_TOKEN`          | Token bot Telegram dari @BotFather                  |
| `SPREADSHEET_ID`          | ID Google Spreadsheet                               |
| `SHEET_GID`               | GID tab spreadsheet (default: `0`)                  |
| `GOOGLE_CREDENTIALS_JSON` | Isi JSON service account (alternatif file `.json`)  |
