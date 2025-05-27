from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
import os

TOKEN = os.getenv("TOKEN")

# Состояния
CHOOSING, PLOT_SIZE, PLOT_BUDGET, HOUSE_ROOMS, HOUSE_FLOORS = range(5)

# Клавиатура выбора
reply_keyboard = [["🏡 Дом", "🌿 Участок"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Что вы ищете?",
        reply_markup=markup
    )
    return CHOOSING

# Обработка выбора
async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    context.user_data["choice"] = choice

    if choice == "🌿 Участок":
        await update.message.reply_text("Введите желаемую площадь участка (в сотках):")
        return PLOT_SIZE
    elif choice == "🏡 Дом":
        await update.message.reply_text("Сколько комнат вы хотите?")
        return HOUSE_ROOMS
    else:
        await update.message.reply_text("Пожалуйста, выберите из меню.")
        return CHOOSING

# Участок: площадь
async def plot_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_size"] = update.message.text
    await update.message.reply_text("Какой у вас бюджет на участок? (в рублях)")
    return PLOT_BUDGET

# Участок: бюджет
async def plot_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plot_budget"] = update.message.text
    await update.message.reply_text(
        f"✅ Вы выбрали участок площадью {context.user_data['plot_size']} соток "
        f"с бюджетом {context.user_data['plot_budget']} руб. Мы подберем варианты!"
    )
    return ConversationHandler.END

# Дом: комнаты
async def house_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["house_rooms"] = update.message.text
    await update.message.reply_text("Сколько этажей вы хотите?")
    return HOUSE_FLOORS

# Дом: этажи
async def house_floors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["house_floors"] = update.message.text
    await update.message.reply_text(
        f"✅ Вы выбрали дом с {context.user_data['house_rooms']} комнатами "
        f"и {context.user_data['house_floors']} этажами. Мы подберем предложения!"
    )
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменен.")
    return ConversationHandler.END

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

# Диалоговый обработчик
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
        PLOT_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_size)],
        PLOT_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_budget)],
        HOUSE_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, house_rooms)],
        HOUSE_FLOORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, house_floors)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()

