import telebot
from telebot import types
from card_tools import make_layout
from chatgpt import prediction
from settings import BOT_MSG_HELLO, BOT_MSG_AWAIT, TELEGRAM_TOKEN, BOT_MSG_ASKME, BOT_MSG_START

bot = telebot.TeleBot(TELEGRAM_TOKEN)
sessions = {}


def add_session(user_id):
    sessions[int(user_id)]: list[dict] = make_layout()


def get_session(user_id):
    return sessions.get(int(user_id), None)


def delete_session(user_id):
    if int(user_id) in sessions.keys():
        del sessions[int(user_id)]


@bot.message_handler(commands=['start'])
def start(message):
    with open("images/cat.png", 'rb') as f:
        photo = f.read()

    msg = bot.send_photo(message.chat.id, photo,
                         caption=BOT_MSG_HELLO.replace("$NAME", message.from_user.first_name))

    # The "Predict" button making
    markup = types.InlineKeyboardMarkup()
    btn_next = types.InlineKeyboardButton('Гадать', callback_data=f"start {message.from_user.id} {message.chat.id}")
    markup.add(btn_next)

    # Binding button to a message
    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg.message_id, reply_markup=markup)


def send_cards(chat_id, card_list, index, user_id):
    if index < len(card_list):
        card = card_list[index]

        with open(card['image'], 'rb') as f:
            photo = f.read()

        msg = bot.send_photo(chat_id, photo, caption=card['prediction'])

        # The "Next" button making
        markup = types.InlineKeyboardMarkup()
        btn_next = types.InlineKeyboardButton('Далее', callback_data=f"{index} {user_id}")
        markup.add(btn_next)

        # Binding button to a message
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg.message_id, reply_markup=markup)
    else:

        bot.send_message(chat_id, card_list[0].get('final_prediction'))
        bot.send_message(chat_id, BOT_MSG_START)

        delete_session(user_id)
        if card_list[0].get('final_prediction', False):
            del card_list[0]['final_prediction']


@bot.message_handler(content_types=["text"])
def question_handler(message):
    if sessions.get(message.from_user.id):
        bot.send_message(message.chat.id, BOT_MSG_AWAIT.replace("$NAME", message.from_user.first_name))

        prediction(layout=sessions[message.from_user.id], question=message.text)

        send_cards(chat_id=message.chat.id, card_list=get_session(message.from_user.id),
                   index=0, user_id=message.from_user.id)

    else:
        bot.send_message(message.chat.id, BOT_MSG_START)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data:
        if call.data.startswith("start"):
            bot.send_message(call.message.chat.id, BOT_MSG_ASKME)
            call_data = call.data.split(" ")
            add_session(call_data[1])

        else:
            call_data = call.data.split(" ")

            if get_session(call_data[1]):
                send_cards(call.message.chat.id, get_session(call_data[1]), int(call_data[0]) + 1,
                           user_id=call_data[1])
                bot.answer_callback_query(call.id)
            else:
                bot.send_message(call.message.chat.id, BOT_MSG_START)


# run bot
bot.polling()
