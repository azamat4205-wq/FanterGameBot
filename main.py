import telebot

bot = telebot.TeleBot("8915110177:AAH5OIpbUQ-PtU2QPVwBWCeqEF_KVatOtc0")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет!")

bot.infinity_polling()
