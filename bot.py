import os

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


DEFAULT_GID = 898337840


async def edit_row(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 6:
            await update.message.reply_text(
                "Format: /editrow <NO> <TGL_CLOSE> <NO_TIKET> <NO_INET> <PERBAIKAN> <TEKNISI>"
            )
            return
        row = int(context.args[0]) + 1  # Tambah 1 agar sesuai baris di sheet
        values = [context.args[0]] + context.args[1:]  # NO tetap sesuai urutan
        creds = Credentials.from_service_account_file(
            "tele-bot-inter-8af7bdb6401f.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key("1XJY7MBlkAcCKThB1uXK4v1jWqtenj5Eu-sLicHqcGfM")
        worksheet = next((ws for ws in sh.worksheets() if ws.id == DEFAULT_GID), None)
        if worksheet is None:
            await update.message.reply_text(
                f"Gagal: Sheet dengan GID {DEFAULT_GID} tidak ditemukan."
            )
            return
        worksheet.update(f"A{row}:F{row}", [values], value_input_option="USER_ENTERED")
        await update.message.reply_text(
            f"Baris {row} di sheet GID {DEFAULT_GID} berhasil diupdate dengan: {values}"
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal update baris: {e} ({type(e)})")


def main():
    if not TOKEN:
        print("Token tidak ditemukan di file .env")
        exit(1)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hai", hai))
    import shlex

    def editrow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = shlex.split(update.message.text)[1:]  # buang /editrow
            context.args = args
            return edit_row(update, context)
        except Exception as e:
            update.message.reply_text(f"Format salah: {e}")

    app.add_handler(CommandHandler("editrow", editrow_handler))
    print("Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()


if __name__ == "__main__":
    main()
