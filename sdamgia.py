from bs4 import BeautifulSoup
import requests
import logging
from config import LOGS


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
    element = soup.find('div', class_='pbody')    # пример класса элемента

    # Извлечение текста из найденного элемента
    text = element.get_text()
    result = text.replace('­', '')
    print(result)
    return result



