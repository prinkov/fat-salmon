import os
from pathlib import Path

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


# --- Web server using aiohttp ---
routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    return web.Response(text="Bot working", content_type="text/plain")

FRONTEND_DIR = Path(__file__).parent / "frontend" / "out"

@routes.get("/app")
async def serve_app(request):
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        return web.Response(text="Frontend not built", status=500)
    return web.FileResponse(index_file)

@routes.get("/app/{path:.*}")
async def serve_static(request):
    path = FRONTEND_DIR / request.match_info["path"]
    if path.is_file():
        return web.FileResponse(path)
    return web.FileResponse(FRONTEND_DIR / "index.html")

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
