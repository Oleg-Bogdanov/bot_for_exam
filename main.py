import telebot
import time
import logging
import schedule
from sdamgia import get_task
from telebot import types
from threading import Thread
from config import LOGS
from creds import get_bot_token
from examiner_database import *
import requests
import pyvips    #библиотека для изменения расширения изображения

bot = telebot.TeleBot(get_bot_token())
create_database()

logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: "
                           "%(funcName)s MESSAGE: %(message)s", filemode="w")

def create_inline_buttons(dictionary: dict):
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
        user_id = int(user_id[0])  # нужен индекс так как функция get_user_ids возвращает список кортежей
        bot.send_message(user_id, 'Пора порешать задания',
                         reply_markup=create_inline_buttons({'получить задание': 'get_task'}))

def schedule_runner():    # Функция, которая запускает бесконечный цикл с расписанием
    while True:    # Уже знакомый тебе цикл
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at("16:00").do(send_task)    # say_hello будет выполняться каждый день в 15:00
Thread(target=schedule_runner).start()

def send_images(links, user_id):
    for i in range(len(links)):
        response = requests.get(url=links[i])
        with open(f"{i}.svg", "wb") as file:
            file.write(response.content)
        image = pyvips.Image.new_from_file(f"{i}.svg", dpi=300)
        image.write_to_file(f"{i}.png")
        bot.send_photo(user_id, open(f"{i}.png", 'rb'))

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
                                       f' тебе напоминание.',
                                  reply_markup=create_inline_buttons({'кнопка': "get_task"}))

        if call.data == 'get_task':
            statistics(user_id)
            task, links = get_task('inf', 'oge', 10875)    # потом придумаем автоматизацию
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                                  text=task)
            send_images(links,user_id)
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, 'произошла непредвиденная ошибка')


bot.infinity_polling(timeout=45)
