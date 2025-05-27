from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
import os

TOKEN = os.getenv("TOKEN")

CHOOSING_STAGE, CHOOSING_PLOT, CONTACT = range(3)

OFFERS = [
    # Добавлены коммуникации
    {'location': '3 этап', 'size': '6 соток', 'price': '3 900 000 ₽', 'utilities': 'электричество, газ, вода, канализация'},
    {"location": "2 этап", "size": "6.92 сотки", "price": "4 498 000 ₽"},
    {"location": "5 этап", "size": "4.9 сотки", "price": "3 185 000 ₽"},
    {"location": "6 этап", "size": "4.75 сотки", "price": "3 087 000 ₽"},
    {"location": "4 этап", "size": "5.5 соток", "price": "2 200 000 ₽"},
    {"location": "4 этап", "size": "6 соток", "price": "2 400 000 ₽"},
    {"location": "коммерция", "size": "20 соток", "price": "10 000 000 ₽"},
    {'location': 'под мкд', 'size': '75 соток', 'price': '37 900 000 ₽', 'utilities': 'электричество, газ, вода, канализация'},
]

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
    keyboard.append([
        InlineKeyboardButton("🔄 Смотреть ещё", callback_data="more"),
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    ])
    keyboard.append([
        InlineKeyboardButton("👤 Связаться с руководителем", url="https://t.me/+79624406464")
    ])

    await query.edit_message_text(
        f"📋 Участки на {stage}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_PLOT

async def more_plots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("stage", "")
    fake_query = update.callback_query
    fake_query.data = stage
    return await show_plots(update, context)

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    return await start(update.callback_query, context)

async def confirm_plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "more":
        return await more_plots(update, context)
    elif query.data == "back":
        return await go_back(update, context)

    size, price = query.data.split("|")
    stage = context.user_data.get("stage", "неизвестный этап")
    context.user_data["plot_info"] = f"{stage}, {size}, {price}"

    await query.edit_message_text(
        f"✅ Вы выбрали участок {size} на {stage} за {price}.

"
        "Пожалуйста, отправьте номер телефона или @username для связи:"
    )
    return CONTACT

async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    plot_info = context.user_data.get("plot_info", "неизвестный участок")
    await update.message.reply_text(
        f"📨 Заявка сохранена!
Участок: {plot_info}
Контакт: {contact}

"
        "Мы свяжемся с вами в ближайшее время 🙏"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

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
