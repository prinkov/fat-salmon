import os
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler
from telegram.request import HTTPXRequest
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = "https://fat-salmon.onrender.com"
PORT = int(os.getenv("PORT", "80"))

# --- Telegram setup ---
requestSet = HTTPXRequest(connection_pool_size=10)
application = Application.builder() \
    .request(requestSet) \
    .token(BOT_TOKEN) \
    .concurrent_updates(False) \
    .build()

async def start(update: Update, context):
    keyboard = [[
        InlineKeyboardButton(
            "🍣 Сделать заказ",
            web_app=WebAppInfo(url=f"{APP_URL}/app")
        )
    ]]
    await update.message.reply_text(
        "Добро пожаловать! Нажми кнопку, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

application.add_handler(CommandHandler("start", start))

# --- Web server using aiohttp ---
routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    return web.Response(text="Bot working", content_type="text/plain")

@routes.get("/app")
async def app_page(request):
    # Можно отдавать реальный index.html из папки
    with open("index.html", encoding="utf-8") as f:
        return web.Response(text=f.read(), content_type="text/html")

@routes.post(f"/{BOT_TOKEN}")
async def webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="ok")

async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")

    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ Bot started, webhook set, serving on port {PORT}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
