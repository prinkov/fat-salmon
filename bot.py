import logging
import mimetypes
import os
import sys
from pathlib import Path

from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler
from telegram.request import HTTPXRequest
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = "https://fat-salmon.onrender.com"
PORT = int(os.getenv("PORT", "80"))

sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Чтобы telegram и aiohttp писали в stdout
logging.getLogger("telegram").setLevel(logging.INFO)
logging.getLogger("telegram.ext").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)

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

application.add_handler(CommandHandler("start", start))


@routes.get("/")
async def index(request):
    return web.Response(text="Bot working !1", content_type="text/plain")

FRONTEND_DIR = Path(__file__).parent / "frontend" / "out"

@routes.get("/app")
async def serve_app(request):
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        return web.Response(text="Frontend not built", status=500)
    return web.FileResponse(index_file)

@routes.get("/_next/{path:.*}")
async def serve_next_static(request):
    path = FRONTEND_DIR / "_next" / request.match_info["path"]
    if path.exists():
        return web.FileResponse(path)
    return web.Response(status=404)

@routes.get(r"/{filename:\w+\.(?:png|jpg|jpeg|gif|webp|svg|ico)}")
async def serve_root_images(request):
    filename = request.match_info["filename"]
    path = FRONTEND_DIR / filename
    if path.exists():
        return web.FileResponse(path)
    return web.Response(status=404)

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
