from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, ConversationHandler, filters
)
from telegram.ext.webhook import WebhookServer
import os

TOKEN = os.getenv("TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # Например: https://your-app.onrender.com
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

SHOWING_PLOTS, CONTACT = range(2)

PLOTS = [
    {
        "photo": "plot1.jpg",
        "stage": "3 этап",
        "size": "6 соток",
        "price": "3 900 000 ₽",
        "utilities": "электричество, газ, вода, канализация"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["index"] = 0
    return await show_plot(update, context)

async def show_plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("index", 0)
    if index >= len(PLOTS):
        await update.message.reply_text("🏁 Участки закончились.")
        return ConversationHandler.END

    plot = PLOTS[index]
    photo = InputFile(plot["photo"])
    caption = (
        "📍 Этап: " + plot["stage"].replace(" этап", "") + "\n"
        "📐 Площадь: " + plot["size"] + "\n"
        "💰 Цена: " + plot["price"] + "\n"
        "🔌 Коммуникации: " + plot["utilities"]
    )
    keyboard = [
        [{"text": "✅ Выбрать", "callback_data": "select"}],
        [{"text": "👤 Руководитель", "url": "https://t.me/+79624406464"}]
    ]
    await update.message.reply_photo(photo=photo, caption=caption)
    return SHOWING_PLOTS

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    plot = context.user_data.get("selected", PLOTS[0])
    msg = (
        "📨 Заявка сохранена!\n"
        "Участок: " + plot.get("stage", "") + ", " + plot.get("size", "") + ", " + plot.get("price", "") + "\n"
        "Контакт: " + contact + "\n\n"
        "Мы свяжемся с вами в ближайшее время 🙏"
    )
    await update.message.reply_text(msg)
    return ConversationHandler.END

async def set_webhook(app):
    await app.bot.set_webhook(WEBHOOK_URL)

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SHOWING_PLOTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact)],
    },
    fallbacks=[]
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook(app))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_path=WEBHOOK_PATH,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL
    )
