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
    values = (our_user_id, "NULL", "NULL", "NULL", "NULL")
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

def select_num_from_database(column, our_user_id): # функция для получения количества решенных и правильно решенных задач
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    query1 = f'''SELECT level, subject FROM users WHERE user_id = {our_user_id} ORDER BY id DESC LIMIT 1'''
    result = cur.execute(query1).fetchall()
    level, subject = result[0][0]
    query2=f'''SELECT {column}  FROM users WHERE user_id = {our_user_id} AND level = {level} AND subject = {subject}'''
    result=cur.execute(query2).fetchall()
    con.close()
    return result[0][0]

def statistics(our_user_id ): #функция для получения всех строк БД, связанных с конкретным пользователем.
    con = sqlite3.connect("examiner_db.sqlite", check_same_thread=False)
    cur = con.cursor()
    query = f'''SELECT * FROM users WHERE user_id = {our_user_id}'''
    result = cur.execute(query).fetchall()
    con.close()
    return result