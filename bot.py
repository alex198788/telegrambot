from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import os

TOKEN = os.getenv("TOKEN")

# Участки до 3.5 млн
PLOTS = [
    {"stage": "5 этап", "size": "4.9 соток", "price": "3 185 000 ₽"},
    {"stage": "6 этап", "size": "4.75 соток", "price": "3 087 000 ₽"},
    {"stage": "4 этап", "size": "5.5 соток", "price": "2 200 000 ₽"},
    {"stage": "4 этап", "size": "6 соток", "price": "2 400 000 ₽"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Добро пожаловать!

"
        "📋 Участки до 3.5 млн:

"
    )
    for plot in PLOTS:
        text += f"🏷 {plot['size']} • {plot['stage']}
💰 {plot['price']} ✅

"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀ Назад", callback_data="back")],
        [InlineKeyboardButton("📲 Связь с руководителем", url="https://t.me/+79624406464")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔙 Вы вернулись в главное меню. Нажмите /start, чтобы начать сначала.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))
    app.run_polling()
