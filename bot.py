import os
from flask import Flask, request, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN", "8439338584:AAEdpDLA1Sehj04KJRtYFTkF6O5R1iwGNI4")
PORT = int(os.getenv("PORT", 8080))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()


# === Telegram команда /start ===
async def start(update: Update, context):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Открыть приложение",
            web_app=WebAppInfo(url=f"https://{request.host}/app")
        )
    ]]
    await update.message.reply_text(
        "Добро пожаловать! Нажми, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


application.add_handler(CommandHandler("start", start))


# === Flask отдаёт фронт ===
@app.route("/app")
def app_page():
    return send_from_directory(".", "index.html")


# === Основной webhook ===
@app.route("/", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Bot running"


# === Запуск ===
if __name__ == "__main__":
    # Не запускаем polling в отдельном потоке — только Flask
    print("Starting webhook Flask app...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/",
        webhook_url=f"https://fat-salmon.onrender.com/"
    )
    app.run(host="0.0.0.0", port=PORT)
