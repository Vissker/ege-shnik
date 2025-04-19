import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = "8086450659:AAFvUNsmSsz8ELTGOTaa6YAo4hsaR27pLlY"

# Загружаем вопросы из файла
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)
# Храним текущую тему и вопрос
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 - ЧИО", callback_data="topic_1")],
        [InlineKeyboardButton("2 - Экономика", callback_data="topic_2")],
        [InlineKeyboardButton("3 - Социология", callback_data="topic_3")],
        [InlineKeyboardButton("4 - Политика", callback_data="topic_4")],
        [InlineKeyboardButton("5 - Право", callback_data="topic_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери тему:", reply_markup=reply_markup)

# Обработка выбора темы
async def topic_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic_num = query.data.split("_")[1]
    user_data[query.from_user.id] = {"topic": topic_num, "question_index": 0}
    await send_question(query, context)

# Отправка вопроса с кнопками
async def send_question(query, context):
    user_id = query.from_user.id
    topic = user_data[user_id]["topic"]
    index = user_data[user_id]["question_index"]
    q = questions[topic][index] #берём вопрос по выбранной теме

    # Кнопки с вариантами ответов
    buttons = []
    for i, option in enumerate(q["options"], start=1):
        buttons.append([InlineKeyboardButton(option, callback_data=f"answer_{i}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(q["question"], reply_markup=reply_markup)
    
# Обработка ответа
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    answer = query.data.split("_")[1]

    topic = user_data[user_id]["topic"]
    index = user_data[user_id]["question_index"]
    q = questions[topic][index]

    if answer == q["correct"]:
        await query.message.reply_text("Верно!")
    else:
        await query.message.reply_text(f"Неверно. Правильный ответ: {q['correct']}")

    # Увеличиваем индекс вопроса
    user_data[user_id]["question_index"] += 1
    next_index = user_data[user_id]["question_index"]

    if next_index < len(questions[topic]):
        # Есть ещё вопросы — задаём следующий
        await send_question(query, context)
    else:
        # Вопросы закончились
        await query.message.reply_text("Ты прошёл все вопросы по этой теме!\nХочешь пройти ещё? Напиши /start")

# Запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(topic_selected, pattern="^topic_"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))

    print("Бот c кнопками запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()