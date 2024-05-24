from bs4 import BeautifulSoup
import requests
import logging
from config import LOGS
import pandas
from PIL import Image

logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: "
                           "%(funcName)s MESSAGE: %(message)s", filemode="w")


def get_task(subject: str, exam: str, task_id: int):
    link = f'https://{subject}-{exam}.sdamgia.ru/problem?id={task_id}'
    # Отправление GET запроса и получение HTML содержимого страницы
    response = requests.get(link)
    html_code = response.text

    # Создание объекта BeautifulSoup
    soup = BeautifulSoup(html_code, "html.parser")

    # Нахождение нужного элемента на странице
    task_element = soup.find('div', class_='pbody')    # пример класса элемента
    sol_element = soup.find('div', class_='solution')

    # Извлечение текста из найденного элемента
    sol_text = sol_element.get_text()
    task_text = task_element.get_text()
    sol = sol_text.replace('­', '')
    task = task_text.replace('­', '')
    print(task, sol)
    return task, sol


# get_task('math', 'oge', 311530)

def get_table(subject: str, exam: str, table_id: int):
    url = f'https://{subject}-{exam}.sdamgia.ru/problem?id={table_id}'
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if table is not None:
        print('Таблица найдена на странице.', table)


# def get_img(subject: str, exam: str, task_id: int):
#     link = f'https://{subject}-{exam}.sdamgia.ru/problem?id={task_id}'
#     # Отправление GET запроса и получение HTML содержимого страницы
#     response = requests.get(link)
#     soup = BeautifulSoup(response.content, 'html.parser')
# # Находим все div с определенным классом
#     div = soup.find('div', class_='pbody')
#     target_tag = div.find('img')
#     # Если нашли тег
#     print(f'https://{subject}-{exam}.sdamgia.ru{target_tag["src"]}')

