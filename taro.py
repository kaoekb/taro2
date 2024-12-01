import telebot
from telebot import types
from card_tools import make_layout
from chatgpt import prediction
from settings import BOT_MSG_HELLO, BOT_MSG_AWAIT, TELEGRAM_TOKEN, BOT_MSG_ASKME, BOT_MSG_START
import logging
import os

log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    filename=os.path.join(log_dir, 'bot_log.log'),  # Логи сохраняются в файл в папке /app/logs
    level=logging.INFO,      # Уровень логирования (INFO и выше)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
sessions = {}


def add_session(user_id):
    logging.info(f"Создание сессии для пользователя {user_id}")
    sessions[int(user_id)] = make_layout()  # исправил на знак равенства


def get_session(user_id):
    session = sessions.get(int(user_id), None)
    if session:
        logging.info(f"Сессия для пользователя {user_id} найдена.")
    else:
        logging.info(f"Сессия для пользователя {user_id} не найдена.")
    return session


def delete_session(user_id):
    if int(user_id) in sessions.keys():
        logging.info(f"Удаление сессии для пользователя {user_id}")
        del sessions[int(user_id)]


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    logging.info(f"Пользователь {user_id} запустил бота (/start).")
    
    with open("images/cat.png", 'rb') as f:
        photo = f.read()

    msg = bot.send_photo(message.chat.id, photo,
                         caption=BOT_MSG_HELLO.replace("$NAME", message.from_user.first_name))

    # Создаем кнопку "Гадать"
    markup = types.InlineKeyboardMarkup()
    btn_next = types.InlineKeyboardButton('Гадать', callback_data=f"start {message.from_user.id} {message.chat.id}")
    markup.add(btn_next)

    # Привязываем кнопку к сообщению
    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg.message_id, reply_markup=markup)


def send_cards(chat_id, card_list, index, user_id):
    if index < len(card_list):
        card = card_list[index]

        with open(card['image'], 'rb') as f:
            photo = f.read()

        msg = bot.send_photo(chat_id, photo, caption=card['prediction'])

        # Создаем кнопку "Далее"
        markup = types.InlineKeyboardMarkup()
        btn_next = types.InlineKeyboardButton('Далее', callback_data=f"{index} {user_id}")
        markup.add(btn_next)

        # Привязываем кнопку к сообщению
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg.message_id, reply_markup=markup)
        logging.info(f"Пользователю {user_id} отправлена карта {index + 1}.")
    else:
        bot.send_message(chat_id, card_list[0].get('final_prediction'))
        bot.send_message(chat_id, BOT_MSG_START)

        delete_session(user_id)
        logging.info(f"Все карты отправлены пользователю {user_id}. Сессия завершена.")

        if card_list[0].get('final_prediction', False):
            del card_list[0]['final_prediction']


@bot.message_handler(content_types=["text"])
def question_handler(message):
    user_id = message.from_user.id
    logging.info(f"Получен текст от пользователя {user_id}: {message.text}")
    
    if sessions.get(user_id):
        bot.send_message(message.chat.id, BOT_MSG_AWAIT.replace("$NAME", message.from_user.first_name))

        logging.info(f"Запуск предсказания для пользователя {user_id}.")
        prediction(layout=sessions[user_id], question=message.text)

        send_cards(chat_id=message.chat.id, card_list=get_session(user_id), index=0, user_id=user_id)
    else:
        logging.info(f"Нет активной сессии для пользователя {user_id}.")
        bot.send_message(message.chat.id, BOT_MSG_START)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data:
        if call.data.startswith("start"):
            logging.info(f"Пользователь {call.from_user.id} нажал кнопку 'Гадать'.")
            bot.send_message(call.message.chat.id, BOT_MSG_ASKME)
            call_data = call.data.split(" ")
            add_session(call_data[1])

        else:
            call_data = call.data.split(" ")
            user_id = call_data[1]

            if get_session(user_id):
                send_cards(call.message.chat.id, get_session(user_id), int(call_data[0]) + 1, user_id=user_id)
                logging.info(f"Пользователь {user_id} нажал 'Далее'. Показана следующая карта.")
                bot.answer_callback_query(call.id)
            else:
                logging.warning(f"Сессия для пользователя {user_id} не найдена при нажатии кнопки.")
                bot.send_message(call.message.chat.id, BOT_MSG_START)


# Запуск бота
logging.info("Запуск бота.")
bot.polling()
