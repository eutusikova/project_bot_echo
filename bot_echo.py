import telebot
import psycopg2
import hashlib
from datetime import datetime, timedelta

#Соединение с тг ботом
bot = telebot.TeleBot("6264956640:AAEXEhZQ7fMW5taqfEUvPd3TzjHKconUtsU")

# установим соединение с бд
def connect_db():
    conn = psycopg2.connect(
        host = "127.0.0.1",
        database = "admin",
        user = "admin",
        password = "root",
        port = "5432"
    )
    return conn

# добавляем в бд пользователя
def message_handler(message, conn):
    user_name = message.from_user.username
    text = message.text
    cursor = conn.cursor()
    cursor.execute('INSERT INTO info_users (user_name, message) VALUES (%s,%s)', (user_name, text))
    conn.commit()

@bot.message_handler(commands = ['start'])
def start(message):
    conn = connect_db()
    cursor = conn.cursor()
    message_handler(message, conn)
    cursor.close()
    conn.close()
    mess = f"Привет, {message.from_user.first_name}. Я бот эхо и отражаю все, что ты пишешь!"
    bot.send_message(message.chat.id, mess)

# выводим бд при получении секрета
@bot.message_handler()
def secret_command_handler(message):
    hash_object = hashlib.md5(message.text.encode('utf-8'))
    if hash_object.hexdigest() == "89de97e8e7ed880d28f477ac8a9c4181":
        conn = connect_db()
        cursor = conn.cursor()
        message_handler(message, conn)
        cursor.execute("""SELECT user_name, MIN(timestamp), MAX(timestamp), 
                    (SELECT message FROM info_users WHERE timestamp = MAX(n.timestamp) and n.user_name = user_name) as message
                    FROM info_users n
                    GROUP BY user_name""")
        info = cursor.fetchall()
        message_text = ""
        flag = 1
        for i in info:
            message_text += f"{flag}; Пользователь: {i[0]}; Время первого сообщения: {format((i[1] + timedelta(hours=3)), '%D %H:%M:%S')}; Время последнего сообщения: {format((i[2] + timedelta(hours=3)), '%D %H:%M:%S')}, Последнее сообщение: {i[3]};\n"
            flag += 1
        bot.send_message(message.chat.id, message_text)
        cursor.close()
        conn.close()
    else:
        conn = connect_db()
        cursor = conn.cursor()
        message_handler(message, conn)
        cursor.close()
        conn.close()
        bot.send_message(message.chat.id, message.text)

# обеспечиваем постоянное обращение к боту
bot.polling(non_stop = True)