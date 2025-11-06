import os
from flask import Flask, request, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = "https://fat-salmon.onrender.com"  # 👈 твой домен Render
PORT = 80

# === Flask ===
app = Flask(__name__)

# === Telegram ===
application = Application.builder().token(BOT_TOKEN).build()

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
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# Проверка доступности
@app.route("/")
def index():
    return "Bot working"

# === Запуск ===
if __name__ == "__main__":
    print("Starting bot via webhook...")
    # Настраиваем webhook у Telegram
    import asyncio
    async def setup():
        await application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")
    asyncio.run(setup())

    # Flask слушает вебхук
    app.run(host="0.0.0.0", port=PORT)