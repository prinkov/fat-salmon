import os
from flask import Flask, send_from_directory, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

# === настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PORT = int(os.getenv("PORT", 3000))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# === Telegram команда /start ===
async def start(update: Update, context):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Открыть приложение",
            web_app=WebAppInfo(url=f"https://{request.host}/app")  # твой фронт
        )
    ]]
    await update.message.reply_text(
        "Добро пожаловать! Нажми, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

application.add_handler(CommandHandler("start", start))

# === Flask отдаёт твой фронт ===
@app.route("/app")
def app_page():
    return send_from_directory(".", "index.html")

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    application.update_queue.put_nowait(Update.de_json(request.get_json(force=True), application.bot))
    return "ok"

@app.route("/")
def index():
    return "Bot running"

# === Запуск ===
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: application.run_polling()).start()
    app.run(host="0.0.0.0", port=PORT)