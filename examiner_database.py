import sqlite3

def create_database():
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    query='''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    level TEXT,
    subject TEXT,
    num_correct_answers INTEGER,
    num_all_answers INTEGER); '''
    cur.execute(query)
    con.close()

def add_user(our_user_id):
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    sql_query = '''INSERT INTO users (user_id, level, subject, num_correct_answers, num_all_answers) VALUES(?, ?, ?, ?, ?);'''
    values = (our_user_id, "NULL", "NULL", 0, 0)
    cur.execute(sql_query, values)
    con.commit()
    con.close()

def update(column, data, our_user_id, ):
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    query1=f'''SELECT Max(id) FROM users WHERE user_id = {our_user_id} ;'''
    result = cur.execute(query1).fetchall()
    max_id=result[0][0]
    print(max_id)
    query2 = f'''UPDATE users SET {column} = "{data}" WHERE user_id = {our_user_id} AND id = {max_id}'''
    cur.execute(query2)
    con.commit()
    con.close()

def select_user_info(column, our_user_id):
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    result = cur.execute(f'''SELECT Max(id) FROM users WHERE user_id = ?''',(our_user_id,)).fetchall()
    max_id = result[0][0]
    result=cur.execute(f'''SELECT {column}  FROM users WHERE user_id = ? AND id = ?''',(our_user_id, max_id)).fetchall()
    con.close()
    return result[0][0]

def statistics(our_user_id, exam, subject): #возвращает количество правильно решенных и всего решенных заданий по конкретному экзамену и предмету
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    num_correct_answers = cur.execute('''SELECT SUM(num_correct_answers)  FROM users WHERE user_id = ? AND level = ? AND subject = ?''', (our_user_id, exam, subject)).fetchall()
    num_all_answers = cur.execute('''SELECT SUM(num_all_answers)  FROM users WHERE user_id = ? AND level = ? AND subject = ?''', (our_user_id, exam, subject)).fetchall()
    con.close()
    return num_correct_answers[0][0], num_all_answers[0][0]


def get_user_ids():    # функция для получения user_id всех пользователей
    # Функция возвращает список кортежей. Типо этого: [(1439318759,), (6459863201,)]
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    query = f'''SELECT DISTINCT user_id FROM users '''
    result = cur.execute(query).fetchall()
    con.close()
    return result

def get_tasks_id(exam, subject):  #функция для получения id всех заданий, возвращает кортежи
    con = sqlite3.connect(f"bank_bot_{exam}.sqlite", check_same_thread=False)
    cur = con.cursor()
    result = cur.execute(f'''SELECT id FROM bank WHERE subject = ?''', (subject,)).fetchall()
    con.close()
    return result

def get_task_solution(id, column, exam): #функция для получения задания или решения или ответа по id
    con = sqlite3.connect(f"bank_bot_{exam}.sqlite", check_same_thread=False)
    cur = con.cursor()
    result = cur.execute(f'''SELECT {column} FROM bank WHERE id = ?''', (id,)).fetchall()
    con.close()
    return result[0][0]

