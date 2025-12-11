import os
import re

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Memuat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Saya adalah bot Telegram sederhana.")


async def hai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user else "teman"
    await update.message.reply_text(f"Hai, {name}!")


SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
DEFAULT_GID = int(os.getenv("SHEET_GID", "0"))


async def format_editrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "Format perintah /edit dan /input:\n\n"
        "/edit <NO> <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>\n"
        "/input <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>\n\n"
        "Contoh:\n"
        '/edit 49 22/1/25 INC42431688 141550108955 "internet baik, pelanggan salah lapor." SUPRI\n'
        '/input 22/1/25 INC42431688 141550108955 "internet baik, pelanggan salah lapor." SUPRI\n\n'
        "Catatan:\n"
        "- <NO> adalah nomor urut data (bukan baris sheet, baris sheet = NO + 1).\n"
        "- <PERBAIKAN> bisa menggunakan kutip jika ada spasi.\n"
        "- Tanggal bisa ditulis singkat (misal: 22/1/25 atau 22/01/25), bot akan otomatis mengubah menjadi 22/01/2025.\n"
        "- Data akan diisi ke kolom A-F pada sheet dengan GID default."
    )
    await update.message.reply_text(txt)


def normalize_date(date_str):
    # Terima format: d/m/yy, dd/mm/yy, d/m/yyyy, dd/mm/yyyy
    match = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", date_str)
    if not match:
        return date_str  # jika tidak cocok, biarkan apa adanya
    day, month, year = match.groups()
    day = day.zfill(2)
    month = month.zfill(2)
    if len(year) == 2:
        year = "20" + year  # asumsikan abad 2000
    return f"{day}/{month}/{year}"


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 6:
            await update.message.reply_text(
                "Format: /edit <NO> <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>"
            )
            return
        row = int(context.args[0]) + 1  # Tambah 1 agar sesuai baris di sheet
        tgl_close = normalize_date(context.args[1])
        values = [context.args[0], tgl_close] + context.args[
            2:
        ]  # NO tetap sesuai urutan
        creds = Credentials.from_service_account_file(
            "tele-bot-inter-8af7bdb6401f.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = next((ws for ws in sh.worksheets() if ws.id == DEFAULT_GID), None)
        if worksheet is None:
            await update.message.reply_text(
                f"Gagal: Sheet dengan GID {DEFAULT_GID} tidak ditemukan."
            )
            return
        worksheet.update(f"A{row}:F{row}", [values], value_input_option="USER_ENTERED")
        await update.message.reply_text(
            f"Baris {row} (NO={context.args[0]}) di sheet GID {DEFAULT_GID} berhasil diupdate dengan: {values}"
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal update baris: {e} ({type(e)})")


async def input_row(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 5:
            await update.message.reply_text(
                "Format: /input <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>"
            )
            return
        creds = Credentials.from_service_account_file(
            "tele-bot-inter-8af7bdb6401f.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = next((ws for ws in sh.worksheets() if ws.id == DEFAULT_GID), None)
        if worksheet is None:
            await update.message.reply_text(
                f"Gagal: Sheet dengan GID {DEFAULT_GID} tidak ditemukan."
            )
            return
        # Cari baris kosong pertama di kolom B (TGL CLOSE)
        col_b = worksheet.col_values(2)
        col_a = worksheet.col_values(1)
        row = None
        no = None
        for i, val in enumerate(col_b[1:], start=2):  # skip header, start=2
            if not val.strip():
                row = i
                if len(col_a) >= i:
                    no = col_a[i - 1]
                else:
                    no = str(i - 1)
                break
        if row is None:
            row = len(col_b) + 1
            no = str(row - 1)
        tgl_close = normalize_date(context.args[0])
        values = [no, tgl_close] + context.args[1:]
        worksheet.update(f"A{row}:F{row}", [values], value_input_option="USER_ENTERED")
        await update.message.reply_text(
            f"Baris baru {row} (NO={no}) di sheet GID {DEFAULT_GID} berhasil diisi dengan: {values}"
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal input baris: {e} ({type(e)})")


def main():
    if not TOKEN:
        print("Token tidak ditemukan di file .env")
        exit(1)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hai", hai))
    app.add_handler(CommandHandler("format", format_editrow))
    import shlex

    def edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = shlex.split(update.message.text)[1:]
            context.args = args
            return edit(update, context)
        except Exception as e:
            update.message.reply_text(f"Format salah: {e}")

    def input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = shlex.split(update.message.text)[1:]
            context.args = args
            return input_row(update, context)
        except Exception as e:
            update.message.reply_text(f"Format salah: {e}")

    app.add_handler(CommandHandler("edit", edit_handler))
    app.add_handler(CommandHandler("input", input_handler))
    print("Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()


if __name__ == "__main__":
    main()
