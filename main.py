import telebot
import time
import schedule
from telebot import types
from config import token
from threading import Thread

bot = telebot.TeleBot(token)


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


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    subject_list = ['rus', 'math', 'inf', 'demos']

    if call.data == 'oge' or call.data == 'ege':
        user_exam = call.message.text    # это текст нажатой кнопки
        print(user_exam)
        # сохрани user_exam в бд ...
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                              text="ты выбрал экзамен, чтобы его поменять воспользуйся командой /new_exam")
        bot.send_message(chat_id=user_id, text='теперь выбери предмет: ',
                         reply_markup=create_inline_buttons(
                             dictionary={'Русский': 'rus',
                                         'Математика': 'math',
                                         'Информатика': 'inf',
                                         'Обществознание': 'demos'}))

    if call.data in subject_list:
        user_choice = call.message.text    # сохрани в бд предмет
        print(user_choice)
        ...
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id,
                              text=f'ты выбрал предмет. '
                                   f'Его всегда можно будет поменять по команде /new_subject.'
                                   f'теперь в 16:00 я буду отправлять'
                                   f' тебе напоминание.')


bot.infinity_polling()
