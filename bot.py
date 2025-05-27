from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import os

TOKEN = os.getenv("TOKEN")

SHOWING_PLOTS, CONFIRM_PLOT, CONTACT = range(3)

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
        [InlineKeyboardButton("✅ Выбрать", callback_data="select")],
        [InlineKeyboardButton("➡ Следующий", callback_data="next")],
        [InlineKeyboardButton("👤 Руководитель", url="https://t.me/+79624406464")]
    ]
    await update.message.reply_photo(photo=photo, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
    return SHOWING_PLOTS

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = context.user_data.get("index", 0)

    if query.data == "next":
        context.user_data["index"] = index + 1
        return await show_plot(query, context)
    elif query.data == "select":
        context.user_data["selected"] = PLOTS[index]
        await query.edit_message_caption(caption="✅ Участок выбран. Пожалуйста, отправьте номер телефона или @username:")
        return CONTACT

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    plot = context.user_data.get("selected", {})
    msg = (
        "📨 Заявка сохранена!\n"
        "Участок: " + plot.get("stage", "") + ", " + plot.get("size", "") + ", " + plot.get("price", "") + "\n"
        "Контакт: " + contact + "\n\n"
        "Мы свяжемся с вами в ближайшее время 🙏"
    )
    await update.message.reply_text(msg)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SHOWING_PLOTS: [CallbackQueryHandler(handle_action)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv_handler)
app.run_polling()
