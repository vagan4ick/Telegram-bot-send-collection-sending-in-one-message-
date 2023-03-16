import telebot
import time
import schedule
import threading


bot_token = 'YOUR_TOKEN_BOT'

# Chat from which we take messages
group_id = YOUR_GROUP_ID

# Chat room where we send messages
source_group_id = YOUR_GROUP_ID

bot = telebot.TeleBot(bot_token)

# In this piece we give the bot a welcome message in case someone decides to write to him personally
@bot.message_handler(content_types=['text'])
def forward_message(message):
    if message.chat.type == 'supergroup':
        if message.chat.id == group_id:
            try:
                bot.send_message(chat_id=source_group_id, reply_to_message_id=message.chat.id)
            except Exception as e:
                print(e)
    else:
        bot.send_message(chat_id=message.chat.id, text="YOUR_TEXT")

messages = []

# Copy and send a message on behalf of the bot
@bot.message_handler(content_types=['text'], func=lambda message: message.chat.type == 'supergroup')
def forward_message(message):
    if message.chat.id != group_id:
        return
    if message.forward_from_chat and message.forward_from_chat.type == 'supergroup':
        return
    if message.reply_to_message:
        return

    messages.append(f"\n\n{message.text}")
    bot.send_message(chat_id=source_group_id, text=message.text+"")

# Combining
def send_all_messages():
    if not messages:
        return
    bot.send_message(chat_id=source_group_id, text="Insert_text_before_sending_all_messages"+"\n".join(list(map(str, messages))))
    messages.clear()


def run_bot_pooling():
    bot.polling(none_stop=True, timeout=0)

#Set the time interval for sending merged messages
def run_scheduler():
    schedule.every().day.at("09:00").do(send_all_messages)
    schedule.every().day.at("15:00").do(send_all_messages)
    schedule.every().day.at("20:00").do(send_all_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    t1 = threading.Thread(target=run_bot_pooling)
    t2 = threading.Thread(target=run_scheduler)
    t1.start()
    t2.start()
