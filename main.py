import json
import os
import re
from datetime import datetime, timedelta, timezone

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Memuat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_GID = int(os.getenv("SHEET_GID", "0"))
SERVICE_ACCOUNT_FILE = os.getenv(
    "SERVICE_ACCOUNT_FILE", "tele-bot-inter-8af7bdb6401f.json"
)
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# Timezone WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

# Regex pattern untuk mendeteksi nomor tiket
# Contoh valid: TKT-001, TICKET-12345, #789, TKT-999, INC42431688
TICKET_PATTERN = re.compile(r"^([A-Za-z]+-?\d+|#\d+)$")


def is_ticket_number(text: str) -> bool:
    """Cek apakah text merupakan nomor tiket yang valid."""
    return bool(TICKET_PATTERN.match(text))


def get_google_sheet():
    """Inisialisasi koneksi ke Google Sheets."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    if GOOGLE_CREDENTIALS_JSON:
        creds_info = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
    gc = gspread.authorize(creds)
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID tidak ditemukan di file .env")
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = next((ws for ws in sh.worksheets() if ws.id == SHEET_GID), None)
    return worksheet


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /close [Nomor Tiket] [Keterangan]"""
    if not update.message:
        return

    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ Format salah!\n"
            "→ Tidak ada nomor tiket dan keterangan.\n\n"
            "Format: /close [Nomor Tiket] [Keterangan]\n"
            "Contoh: /close TKT-001 Masalah sudah selesai"
        )
        return

    first_arg = args[0]
    rest_args = args[1:]

    # Argumen pertama bukan nomor tiket (langsung keterangan tanpa tiket)
    if not is_ticket_number(first_arg):
        await update.message.reply_text(
            "❌ Format salah!\n"
            "→ Tidak ada nomor tiket.\n\n"
            "Format: /close [Nomor Tiket] [Keterangan]\n"
            "Contoh: /close TKT-001 Masalah sudah selesai"
        )
        return

    # Ada nomor tiket tapi tidak ada keterangan
    if not rest_args:
        await update.message.reply_text(
            "❌ Format salah!\n"
            "→ Tidak ada keterangan.\n\n"
            "Format: /close [Nomor Tiket] [Keterangan]\n"
            "Contoh: /close TKT-001 Masalah sudah selesai"
        )
        return

    nomor_tiket = first_arg
    keterangan = " ".join(rest_args)

    # Data user
    user = update.effective_user
    nama_user = user.full_name if user else "Unknown"

    # Timestamp WIB
    timestamp = datetime.now(WIB).strftime("%d/%m/%Y %H:%M:%S")

    # Tulis ke Google Sheets
    try:
        worksheet = get_google_sheet()
        if worksheet is None:
            await update.message.reply_text(
                f"❌ Gagal: Sheet dengan GID {SHEET_GID} tidak ditemukan."
            )
            return

        row_data = [timestamp, nama_user, nomor_tiket, keterangan]
        worksheet.append_row(row_data, value_input_option=ValueInputOption.user_entered)

        await update.message.reply_text(
            f"✅ Tiket berhasil di-close!\n\n"
            f"🕐 Timestamp: {timestamp}\n"
            f"👤 Nama User: {nama_user}\n"
            f"📋 Nomor Tiket: {nomor_tiket}\n"
            f"📝 Keterangan: {keterangan}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menyimpan data: {e}")


def main():
    if not TOKEN:
        print("Token tidak ditemukan di file .env")
        exit(1)

    if not SPREADSHEET_ID:
        print("SPREADSHEET_ID tidak ditemukan di file .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("close", close))

    print("Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()


if __name__ == "__main__":
    main()
