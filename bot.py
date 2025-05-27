from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
import os

TOKEN = os.getenv("TOKEN")

# Conversation states
CHOOSING, PLOT_SIZE, PLOT_BUDGET, PLOT_LOCATION, PLOT_CONTACT = range(5)

# Reply keyboard
reply_keyboard = [["🌿 Участок", "🏡 Дом"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добрый день! Вы ищете дом или участок?",
        reply_markup=markup
    )
    return CHOOSING

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🌿 Участок":
        await update.message.reply_text("Введите желаемую площадь участка (в сотках):")
        return PLOT_SIZE
    else:
        await update.message.reply_text("На данный момент доступны только участки 🌿")
        return ConversationHandler.END

async def plot_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_size"] = update.message.text
    await update.message.reply_text("Какой у вас бюджет? (в рублях)")
    return PLOT_BUDGET

async def plot_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_budget"] = update.message.text
    await update.message.reply_text("Укажите желаемый район или населённый пункт:")
    return PLOT_LOCATION

async def plot_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_location"] = update.message.text

    # Simulated offers
    offers = """Вот что мы можем вам предложить:

🏷 Участок 10 соток
📍 Село Александровское
💰 950,000 ₽
💡 Электричество, газ рядом

🏷 Участок 12 соток
📍 Село Надежда
💰 1,150,000 ₽
🌿 ИЖС, участок ровный
"""
    await update.message.reply_text(offers)
    await update.message.reply_text("Оставьте, пожалуйста, номер телефона или @username для связи:")
    return PLOT_CONTACT

async def plot_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_contact"] = update.message.text
    await update.message.reply_text(
        "✅ Спасибо! Мы свяжемся с вами в ближайшее время 🙏"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

# Initialize app
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
        PLOT_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_size)],
        PLOT_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_budget)],
        PLOT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_location)],
        PLOT_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
