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
import random


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


schedule.every().day.at("12:00").do(send_task)    # say_hello будет выполняться каждый день в 15:00
Thread(target=schedule_runner).start()


@bot.message_handler(commands=['get_exercise'])
def send_exercise(message):
    user_id = message.chat.id
    print(user_id)
    user_exam = select_user_info('level', user_id)
    print(user_exam)
    subject = select_user_info('subject', user_id)
    print(subject)
    exercises = get_tasks_id(user_exam, subject)
    exer = random.choice(exercises)
    exer = int(exer[0])
    task = get_task_solution(exer, 'task', user_exam)
    if task != "NULL":
        bot.send_message(message.chat.id, task)
    task_img = get_task_solution(exer, 'task_img', user_exam)
    if task_img != "NULL":
        bot.send_photo(message.chat.id, photo=open(f'images/{task_img}', 'rb'))
    bot.register_next_step_handler(message, check_answer, exer, user_exam, user_id)

def check_answer(message, exer, user_exam, user_id):
    user_answer = message.text
    right_answer = get_task_solution(exer, 'answer', user_exam)
    cor=select_user_info("num_correct_answers",user_id)
    all=select_user_info("num_all_answers",user_id)
    if user_answer == right_answer:
        bot.send_message(message.chat.id, "Всё верно!")
        a=cor+1
        b=all+1
        update("num_correct_answers", a, user_id)
        update("num_all_answers", b, user_id)
    else:
        bot.send_message(message.chat.id, "Ответ неверен")
        a = cor + 0
        b = all + 1
        update("num_correct_answers", a, user_id)
        update("num_all_answers", b, user_id)
    solution = get_task_solution(exer, 'solution', user_exam)
    if solution != "NULL":
        bot.send_message(message.chat.id, solution)
    solution_image = get_task_solution(exer, 'solution_image', user_exam)
    if solution_image != "NULL":
        bot.send_photo(message.chat.id, photo=open(f'images/{solution_image}', 'rb'))
    bot.send_message(message.chat.id, "Чтобы получить следующее задание, используйте команду /get_exercise")




@bot.message_handler(commands=['update_exam'])
def update_exam(message):
    bot.send_message(message.chat.id, 'выбери экзамен:',
                     reply_markup=create_inline_buttons(dictionary=
                                                        {'Готовиться к ОГЭ': 'oge',
                                                         'Готовиться к ЕГЭ': 'ege'}))


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    subject_list = ['rus', 'math', 'his']
    #try:
    if call.data == 'oge' or call.data == 'ege':
        user_exam = call.data   # это текст нажатой кнопки
        add_user(user_id)                             # я хочу хранить информацию о всех предметах пользователя,
        update("level", user_exam, user_id)    # поэтому в базе будет несколько строк с одним id, но разными предметами
        # сохрани user_exam в бд ...                  # и экзаменами
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                              text="Ты выбрал экзамен, чтобы его поменять воспользуйся командой /update_exam")
        bot.send_message(chat_id=user_id, text='Теперь выбери предмет: ',
                         reply_markup=create_inline_buttons(
                             dictionary={'Русский': 'rus',
                                         'Математика': 'math',
                                         'История': 'his'}))

    if call.data in subject_list:
        user_choice = call.data    # сохрани в бд предмет
        update("subject", user_choice, user_id)
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                              text=f'Ты выбрал предмет. '
                                   f'Его всегда можно будет поменять по команде /update_exam.'
                                   f'Теперь в 12:00 я буду отправлять'
                                   f' тебе напоминание.',
                              reply_markup=create_inline_buttons({'Получить задание': "get_task"}))

    if call.data == 'get_task':
        send_exercise(call.message)
    # except Exception as e:
    #     logging.error(e)
    #     bot.send_message(user_id, 'произошла непредвиденная ошибка')

@bot.message_handler(commands=['statistics'])
def send_statistics(message):
    user_id = message.chat.id
    print(user_id)
    user_exam = select_user_info('level', user_id)
    print(user_exam)
    subject = select_user_info('subject', user_id)
    cor, all= statistics(user_id, user_exam, subject)
    bot.send_message(user_id, f"Экзамен: {user_exam}\n"
                                   f"Предмет: {subject}\n"
                                   f"Правильно решено: {cor}\n"
                                   f"Всего решено: {all}\n")



bot.infinity_polling(timeout=45)
