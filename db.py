import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# СОЗДАНИЕ ТАБЛИЦЫ

# cursor.execute('''
# CREATE TABLE data (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     email TEXT,
#     phone TEXT
# );
# ''')

# ДОБАВЛЕНИЕ ДАННЫХ
cursor.execute('''
INSERT INTO data (name, email, phone) VALUES
    ('Test 1', 'test1@example.com', '+7 777 777 7777'),
    ('Test 2', 'test2@example.com', '+7 777 777 8888'),
    ('Test 3', 'test3@example.com', '+7 777 777 9999');
''')
conn.commit()
conn.close()