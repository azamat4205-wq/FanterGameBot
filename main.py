import telebot

bot = telebot.TeleBot("8915110177:AAH1vTla4PHAPYy_SY22aywNB34o7UZ9YMI")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет!")

bot.infinity_polling()
