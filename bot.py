import os
from flask import Flask, request, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler
from telegram.request import HTTPXRequest

BOT_TOKEN = os.getenv("BOT_TOKEN", "8439338584:AAEdpDLA1Sehj04KJRtYFTkF6O5R1iwGNI4")
APP_URL = "https://fat-salmon.onrender.com"  # 👈 твой домен Render
PORT = 80

# === Flask ===
app = Flask(__name__)


requestSet = HTTPXRequest(
    connection_pool_size=10,
    connect_timeout=20,
    read_timeout=20,
    write_timeout=20,
    pool_timeout=10,
)
application = Application.builder().request(requestSet).token(BOT_TOKEN).concurrent_updates(False).build()

# /start — одна кнопка
async def start(update: Update, context):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Открыть приложение",
            web_app=WebAppInfo(url=f"{APP_URL}/app")
        )
    ]]
    await update.message.reply_text(
        "Добро пожаловать! Нажми кнопку, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

application.add_handler(CommandHandler("start", start))

# === Страница приложения ===
@app.route("/app")
def app_page():
    return send_from_directory(".", "index.html")

# === Webhook endpoint ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    import asyncio
    asyncio.run(application.process_update(update))
    return "ok", 200

@app.route("/")
def index():
    return "Bot working"

if __name__ == "__main__":
    print("Starting bot via webhook...")
    import asyncio
    async def setup():
        await application.initialize()
        await application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")
    asyncio.run(setup())

    app.run(host="0.0.0.0", port=PORT)