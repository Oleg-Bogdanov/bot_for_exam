from bs4 import BeautifulSoup
import requests
import logging
from config import LOGS
#import pandas
#from PIL import Image


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

    # Извлечение текста из найденного элемента
    task_text = task_element.get_text()
    task = task_text.replace('­', '')
    task_images = soup.find('div', class_='pbody').find_all("img") # находим все изображения в условии задания
    if len(task_images) != 0:
        links = [] #список ссылок на изображения
        for i in range(len(task_images)):
            links.append(task_images[i].get('src')) #получаем ссылки

        for n in range(len(links)):
            if "https" not in links[n]: #изменяем неполные ссылки
                links[n] = f'https://{subject}-{exam}.sdamgia.ru{links[n]}'
    else:
        links=[]
    print(links)
    return task, links

#разбила get_task и get_solution на две функции, мне так удобнее

def get_solution(subject: str, exam: str, task_id: int): #не редактировала
    link = f'https://{subject}-{exam}.sdamgia.ru/problem?id={task_id}'
    # Отправление GET запроса и получение HTML содержимого страницы
    response = requests.get(link)
    html_code = response.text

    # Создание объекта BeautifulSoup
    soup = BeautifulSoup(html_code, "html.parser")

    # Нахождение нужного элемента на странице
    # пример класса элемента
    sol_element = soup.find('div', class_='solution')

    # Извлечение текста из найденного элемента
    #sol_text = sol_element.get_text()

    #sol = sol_text.replace('­', '')
    print(sol_element)
    return sol_element


# <<<<<<< HEAD
# # get_task('math', 'oge', 311530)
# =======
# get_solution('math', 'ege', 27238)
# >>>>>>> 123b74b0e72075041b481dea9a0c788b000b4257

def get_table(subject: str, exam: str, table_id: int):
    url = f'https://{subject}-{exam}.sdamgia.ru/problem?id={table_id}'
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if table is not None:
        print('Таблица найдена на странице.', table)

# функцию отправки изображений перенесла в файл main


