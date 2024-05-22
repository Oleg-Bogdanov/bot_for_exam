import telebot
import time
import schedule
from telebot import types
from examiner_database import create_database, add_user, update, select_num_from_database, statistics
from threading import Thread
from creds import get_bot_token
from examiner_database import *

bot = telebot.TeleBot(get_bot_token())
create_database()

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
        bot.send_message(user_id, 'Привет, это бот для подготовки к ОГЭ и ЕГЭ. '
                                  'Выбери, к чему ты готовишься, нажав на кнопки',
                                  reply_markup=create_inline_buttons({'Готовиться к ОГЭ': 'oge',
                                                                      'Готовиться к ЕГЭ': 'ege'}))
        # в key пишем текст кнопки, а к value callback_data
    except Exception as e:
        bot.send_message(user_id, f'{e}')


def send_task():
    user_id = 1439318759    # Идентификатор пользователя, которому отправляем сообщение. Замени на свой
    bot.send_message(user_id, 'Пора порешать задания',
                     reply_markup=create_inline_buttons({'получить задание📖': 'get_task'}))

def schedule_runner():    # Функция, которая запускает бесконечный цикл с расписанием
    while True:    # Уже знакомый тебе цикл
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at("15:00").do(send_task)    # say_hello будет выполняться каждый день в 15:00
Thread(target=schedule_runner).start()

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    subject_list = ['rus', 'math', 'inf', 'demos']

    if call.data == 'oge' or call.data == 'ege':
        user_exam = call.message.text    # это текст нажатой кнопки
        print("user_exam:", user_exam)
        add_user(user_id)
        update("level", user_exam, user_id)
        # сохрани user_exam в бд ...
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                              text="Ты выбрал экзамен, чтобы его поменять воспользуйся командой /new_exam")
        bot.send_message(chat_id=user_id, text='Теперь выбери предмет: ',
                         reply_markup=create_inline_buttons(
                             dictionary={'Русский✒': 'rus',
                                         'Математика': 'math',
                                         'Информатика': 'inf',
                                         'Обществознание': 'demos'}))

    if call.data in subject_list:
        user_choice = call.message.text    # сохрани в бд предмет
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


bot.infinity_polling()
