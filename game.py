from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
from questions import questions  # Import questions from questions.py

current_question = {}
current_answers = {}
user_scores = {}
bot_message_ids = []

# Fungsi untuk memulai bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selamat datang di Family 100! Ketik /play untuk memulai permainan.")

# Fungsi untuk memulai permainan
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_question, current_answers, bot_message_ids
    current_question = random.choice(questions)
    current_answers = {i+1: None for i in range(len(current_question["answers"]))}
    question_text = f"{current_question['question']}\n\n"
    for i in range(1, len(current_answers)+1):
        question_text += f"{i}. ???\n"
    message = await update.message.reply_text(question_text)
    bot_message_ids.append(message.message_id)

# Fungsi untuk mengakhiri permainan
async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_question, current_answers, bot_message_ids
    current_question = {}
    current_answers = {}
    leaderboard = "Permainan Berakhir! Peringkat Skor Pemain:\n"
    for user in sorted(user_scores.values(), key=lambda x: x['score'], reverse=True):
        leaderboard += f"@{user['name']}: {user['score']} poin\n"
    await update.message.reply_text(leaderboard)
    for msg_id in bot_message_ids:
        try:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg_id)
        except Exception as e:
            print(f"Failed to delete message {msg_id}: {e}")
    bot_message_ids = []
    user_scores.clear()

# Fungsi untuk menangani jawaban
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_question, current_answers, bot_message_ids
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or "Anonim"  # Gunakan username atau Anonim jika tidak ada
    user_answer = update.message.text.lower()

    if current_question:
        correct_answers = [answer.lower() for answer in current_question["answers"]]
        if user_answer in correct_answers:
            answer_index = correct_answers.index(user_answer) + 1
            if current_answers[answer_index] is None:
                current_answers[answer_index] = current_question["answers"][answer_index-1]
                if user_id not in user_scores:
                    user_scores[user_id] = {'score': 0, 'name': user_name}
                user_scores[user_id]['score'] += 1
                
                # Tampilkan papan dengan jawaban yang sudah terbuka
                question_text = f"{current_question['question']}\n\n"
                for i in range(1, len(current_answers)+1):
                    if current_answers[i]:
                        question_text += f"{i}. {current_answers[i]}\n"
                    else:
                        question_text += f"{i}. ???\n"
                        
                message = await update.message.reply_text(f"Yoi betul bro! Skor Anda: {user_scores[user_id]['score']}\n\n{question_text}")
                bot_message_ids.append(message.message_id)
                
                # Cek jika semua jawaban sudah terbuka
                if all(current_answers.values()):
                    leaderboard = "Peringkat Skor Pemain:\n"
                    for user in sorted(user_scores.values(), key=lambda x: x['score'], reverse=True):
                        leaderboard += f"@{user['name']}: {user['score']} poin\n"
                    await update.message.reply_text("Semua jawaban benar! Ketik /lanjut untuk pertanyaan selanjutnya.\n\n" + leaderboard)
                    
                    for msg_id in bot_message_ids:
                        try:
                            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg_id)
                        except Exception as e:
                            print(f"Failed to delete message {msg_id}: {e}")
                    bot_message_ids = []
                    current_question = {}
                    current_answers = {}
            else:
                await update.message.reply_text("Ga salah sih cuma dah pernah cog!")
        else:
            await update.message.reply_text("Salah gblk ;v")

# Fungsi untuk melanjutkan permainan
async def lanjut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play(update, context)

# Konfigurasi Bot
if __name__ == '__main__':
    bot_token = '8039799886:AAFlhDioZJ0WtQNO53wY7HVUga_IpWPAeoc'
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("lanjut", lanjut))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("Bot sedang berjalan...")
    app.run_polling()
