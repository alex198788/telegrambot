from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler
)
import os

TOKEN = os.getenv("TOKEN")

CHOOSE_STAGE, CHOOSE_SIZE = range(2)

PLOTS = {
    "3 этап": [("6 соток", "3 900 000 ₽")],
    "2 этап": [("6.92 соток", "4 498 000 ₽")],
    "5 этап": [("4.9 соток", "3 185 000 ₽")],
    "6 этап": [("4.75 соток", "3 087 000 ₽")],
    "4 этап": [("5.5 соток", "2 200 000 ₽"), ("6 соток", "2 400 000 ₽")],
    "Коммерция": [("20 соток", "10 000 000 ₽")],
    "Под МКД": [("75 соток", "37 900 000 ₽")]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_stages = sorted(PLOTS.keys(), key=lambda x: int(x.split()[0]) if x.split()[0].isdigit() else 999)
    keyboard = [[InlineKeyboardButton(stage, callback_data=stage)] for stage in sorted_stages]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 Добро пожаловать!\n\nВыберите участок:",)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

    return CHOOSE_STAGE

async def choose_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stage = query.data
    context.user_data["stage"] = stage

    sizes = list({s for s, _ in PLOTS[stage]})
    keyboard = [[InlineKeyboardButton(size, callback_data=size)] for size in sizes]
    keyboard.append([InlineKeyboardButton("◀ Назад", callback_data="back_to_start")])
    await query.edit_message_text(
        f"Вы выбрали: {stage}\nТеперь выберите площадь:", 
    reply_markup=InlineKeyboardMarkup(keyboard)
)
    return CHOOSE_SIZE

async def show_plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stage = context.user_data["stage"]
    size = query.data

    for s, price in PLOTS[stage]:
        if s == size:
            selected_price = price
            break
    else:
        selected_price = "—"

    text = (
        f"🏡 Участок выбран:
"
        f"📍 Этап: {stage.replace(' этап', '')}
"
        f"📐 Площадь: {size}
"
        f"💰 Цена: {selected_price}
"
        f"🔌 Коммуникации: электричество, газ, вода, канализация"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Связаться с руководителем", url="https://t.me/+79624406464")],
        [InlineKeyboardButton("◀ Назад", callback_data="back_to_stage")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)
    return ConversationHandler.END

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_start":
        return await start(query, context)
    elif query.data == "back_to_stage":
        return await choose_stage(query, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_STAGE: [CallbackQueryHandler(choose_stage, pattern="^(?!back_to_).*")],
            CHOOSE_SIZE: [CallbackQueryHandler(show_plot, pattern="^(?!back_to_).*")],
        },
        fallbacks=[
            CallbackQueryHandler(go_back, pattern="^back_to_.*")
        ]
    )

    app.add_handler(conv)
    app.run_polling()
