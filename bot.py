from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
import os

TOKEN = os.getenv("TOKEN")

# Состояния диалога
CHOOSING_STAGE, CHOOSING_PLOT, CONTACT = range(3)

# Участки (предложения)
OFFERS = [
    {"location": "3 этап", "size": "6 соток", "price": "3 900 000 ₽"},
    {"location": "2 этап", "size": "6.92 сотки", "price": "4 498 000 ₽"},
    {"location": "5 этап", "size": "4.9 сотки", "price": "3 185 000 ₽"},
    {"location": "6 этап", "size": "4.75 сотки", "price": "3 087 000 ₽"},
    {"location": "4 этап", "size": "5.5 соток", "price": "2 200 000 ₽"},
    {"location": "4 этап", "size": "6 соток", "price": "2 400 000 ₽"},
    {"location": "коммерция", "size": "20 соток", "price": "10 000 000 ₽"},
    {"location": "под мкд", "size": "75 соток", "price": "37 900 000 ₽"},
]

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("3 этап", callback_data="3 этап"),
         InlineKeyboardButton("4 этап", callback_data="4 этап")],
        [InlineKeyboardButton("5 этап", callback_data="5 этап"),
         InlineKeyboardButton("6 этап", callback_data="6 этап")],
        [InlineKeyboardButton("Коммерция", callback_data="коммерция"),
         InlineKeyboardButton("Под МКД", callback_data="под мкд")]
    ]
    await update.message.reply_text(
        "📍 Выберите этап или категорию участков:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_STAGE

# Показ участков
async def show_plots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stage = query.data
    context.user_data["stage"] = stage

    matched = [o for o in OFFERS if o["location"] == stage]
    if not matched:
        await query.edit_message_text("😔 Участков на этом этапе пока нет.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(f"{o['size']} — {o['price']}", callback_data=f"{o['size']}|{o['price']}")]
        for o in matched
    ]

    await query.edit_message_text(
        f"📋 Участки на {stage}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_PLOT

# Подтверждение выбора участка
async def confirm_plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    size, price = query.data.split("|")
    stage = context.user_data.get("stage", "неизвестно")

    context.user_data["plot_info"] = f"{stage}, {size}, {price}"

    await query.edit_message_text(
        f"✅ Вы выбрали участок {size} на {stage} за {price}.\n\n"
        "Пожалуйста, отправьте номер телефона или @username для связи:"
    )
    return CONTACT

# Обработка контакта
async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    plot_info = context.user_data.get("plot_info", "неизвестно")
    await update.message.reply_text(
        f"📨 Заявка сохранена!\nУчасток: {plot_info}\nКонтакт: {contact}\n\n"
        "Мы свяжемся с вами в ближайшее время 🙏"
    )
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_STAGE: [CallbackQueryHandler(show_plots)],
        CHOOSING_PLOT: [CallbackQueryHandler(confirm_plot)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_contact)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv_handler)
app.run_polling()
