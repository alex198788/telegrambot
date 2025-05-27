from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
import os

TOKEN = os.getenv("TOKEN")

# States
CHOOSING, PLOT_SIZE, PLOT_BUDGET, PLOT_LOCATION, PLOT_CONTACT = range(5)

# Offer list
OFFERS = [
    {"location": "3 этап", "size": "6 соток", "price": "3 900 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "2 этап", "size": "6.92 сотки", "price": "4 498 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "5 этап", "size": "4.9 сотки", "price": "3 185 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "6 этап", "size": "4.75 сотки", "price": "3 087 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "4 этап", "size": "5.5 соток", "price": "2 200 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "4 этап", "size": "6 соток", "price": "2 400 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "коммерция", "size": "20 соток", "price": "10 000 000 ₽", "utilities": "Электр., газ, вода, канализация"},
    {"location": "под мкд", "size": "75 соток", "price": "37 900 000 ₽", "utilities": "Электр., газ, вода, канализация"},
]

# Keyboards
start_keyboard = [["📋 Получить подборку"]]
location_keyboard = [
    ["3 этап", "4 этап"],
    ["5 этап", "6 этап"],
    ["Коммерция", "Под МКД"]
]

markup_start = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)
markup_location = ReplyKeyboardMarkup(location_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добрый день! Что вы хотите сделать?",
        reply_markup=markup_start
    )
    return CHOOSING

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "подборку" in text.lower():
        await update.message.reply_text("Введите желаемую площадь участка (в сотках):")
        return PLOT_SIZE
    else:
        await update.message.reply_text("Выберите действие с клавиатуры.")
        return CHOOSING

async def plot_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_size"] = update.message.text
    await update.message.reply_text("Какой у вас бюджет? (в рублях)")
    return PLOT_BUDGET

async def plot_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_budget"] = update.message.text
    await update.message.reply_text("Выберите район или категорию участка:", reply_markup=markup_location)
    return PLOT_LOCATION

async def plot_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text.strip().lower()
    context.user_data["plot_location"] = location

    matched_offers = [o for o in OFFERS if o["location"].lower() in location]

    if matched_offers:
        response = "Вот что мы можем вам предложить:

"
        for offer in matched_offers:
            response += (
                f"🏷 Участок {offer['size']}
"
                f"📍 Район: {offer['location']}
"
                f"💰 {offer['price']}
"
                f"🔌 Коммуникации: {offer['utilities']}

"
            )
    else:
        response = "😔 Пока нет участков в этом районе или категории. Мы постараемся подобрать для вас подходящий вариант!"

    await update.message.reply_text(response)
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

# App setup
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
