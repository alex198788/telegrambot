from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import os

TOKEN = os.getenv("TOKEN")

SHOWING_PLOTS, CONTACT = range(2)

PLOTS = [
    {
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
    caption = (
        f"📍 Этап: {plot['stage'].replace(' этап', '')}
"
        f"📐 Площадь: {plot['size']}
"
        f"💰 Цена: {plot['price']}
"
        f"🔌 Коммуникации: {plot['utilities']}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Выбрать", callback_data="select")],
        [InlineKeyboardButton("👤 Руководитель", url="https://t.me/+79624406464")]
    ])
    await update.message.reply_text(text=caption, reply_markup=keyboard)
    return SHOWING_PLOTS

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["selected"] = PLOTS[0]
    await query.edit_message_text(text="✅ Участок выбран. Пожалуйста, отправьте номер телефона или @username:")
    return CONTACT

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    plot = context.user_data.get("selected", PLOTS[0])
    msg = (
        f"📨 Заявка сохранена!
"
        f"Участок: {plot.get('stage', '')}, {plot.get('size', '')}, {plot.get('price', '')}
"
        f"Контакт: {contact}

"
        "Мы свяжемся с вами в ближайшее время 🙏"
    )
    await update.message.reply_text(msg)
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SHOWING_PLOTS: [CallbackQueryHandler(handle_action)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_polling()
