import telebot
import time
import logging
import schedule
from telebot import types
from examiner_database import create_database, \
    add_user, update, select_num_from_database, statistics, get_user_ids
from threading import Thread
from config import LOGS
from creds import get_bot_token
from examiner_database import *

bot = telebot.TeleBot(get_bot_token())
create_database()

logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: "
                           "%(funcName)s MESSAGE: %(message)s", filemode="w")

def create_inline_buttons(dictionary):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for key, value in dictionary.items():
        callback_button = types.InlineKeyboardButton(text=key, callback_data=value)
        keyboard.add(callback_button)

    return keyboard


@bot.message_handler(commands=['start'])
def start_dialog(message):
    user_id = message.from_user.id
    try:
        current_users = get_user_ids()
        users_list = [item[0] for item in current_users]
        if user_id not in users_list:
            add_user(our_user_id=user_id)
        bot.send_message(user_id, 'Привет, это бот для подготовки к ОГЭ и ЕГЭ. '
                                  'Выбери, к чему ты готовишься, нажав на кнопки',
                                  reply_markup=create_inline_buttons({'Готовиться к ОГЭ': 'oge',
                                                                      'Готовиться к ЕГЭ': 'ege'}))
        # в key пишем текст кнопки, а к value callback_data
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, 'произошла ошибка, попробуйте позже')


def send_task():
    id_list = get_user_ids()    # Идентификатор пользователя, которому отправляем сообщение. Замени на свой
    for user_id in id_list:
        user_id = int(user_id)
        bot.send_message(user_id, 'Пора порешать задания',
                         reply_markup=create_inline_buttons({'получить задание': 'get_task'}))

def schedule_runner():    # Функция, которая запускает бесконечный цикл с расписанием
    while True:    # Уже знакомый тебе цикл
        schedule.run_pending()
        time.sleep(1)


# schedule.every(10).seconds.do(send_task)
schedule.every().day.at("17:15").do(send_task)    # say_hello будет выполняться каждый день в 15:00
Thread(target=schedule_runner).start()

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    subject_list = ['rus', 'math', 'inf', 'demos']
    try:
        if call.data == 'oge' or call.data == 'ege':
            user_exam = call.data   # это текст нажатой кнопки
            print("user_exam:", call.data)
            update("level", user_exam, user_id)
            # сохрани user_exam в бд ...
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                  text="Ты выбрал экзамен, чтобы его поменять воспользуйся командой /new_exam")
            bot.send_message(chat_id=user_id, text='Теперь выбери предмет: ',
                             reply_markup=create_inline_buttons(
                                 dictionary={'Русский': 'rus',
                                             'Математика': 'math',
                                             'Информатика': 'inf',
                                             'Обществознание': 'demos'}))

        if call.data in subject_list:
            user_choice = call.data    # сохрани в бд предмет
            print(user_choice)
            update("subject", user_choice, user_id)
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                  text=f'Ты выбрал предмет. '
                                       f'Его всегда можно будет поменять по команде /new_subject.'
                                       f'Теперь в 16:00 я буду отправлять'
                                       f' тебе напоминание.')

        if call.data == 'get_task':
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                  text='тут будет задание')
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, 'произошла непредвиденная ошибка')


bot.infinity_polling()
