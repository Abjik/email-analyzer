import sqlite3
import json
import yaml
import imaplib
import email

# Загрузка конфигурации
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Установка соединения с почтовым сервером
mail = imaplib.IMAP4_SSL(config['imap_server'])
mail.login(config['email_address'], config['password'])
mail.select('inbox')  # Выбор почтового ящика

# Создание соединения с базой данных
with sqlite3.connect(config['db_path']) as conn:
    cursor = conn.cursor()

    # Создание таблицы, если она еще не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        name TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    # Обработка сообщений
    for email_id in mail.search(None, '(UNSEEN)')[1][0].split():
        # Получение данных сообщения
        message_data = mail.fetch(email_id, '(BODY.PEEK[])')
        if message_data[0] is None:
            continue

        raw_email = message_data[0][1]
        if isinstance(raw_email, bytes):
            raw_email = raw_email.decode("utf-8")

        email_message = email.message_from_string(raw_email)

        # Проверка отправителя
        from_header = email_message.get('From')
        if from_header is None or not any(trigger in from_header for trigger in config['trigger_recipients']):
            continue    

        # Проверка формата сообщения и извлечение данных
        email_data = {}
        if email_message.is_multipart():
            for payload in email_message.get_payload():
                body = payload.get_payload(decode=True)
                try:
                    email_data.update(json.loads(body))
                except json.JSONDecodeError:
                    continue
        else:
            body = email_message.get_payload(decode=True)
            try:
                email_data.update(json.loads(body))
            except json.JSONDecodeError:
                continue

        # Проверка наличия данных в базе
        name = email_data.get('name')
        email = email_data.get('email')
        if name is None or email is None:
            continue

        cursor.execute("SELECT * FROM data WHERE name = ? AND email = ?", (name, email))
        if cursor.fetchone() is not None:
            continue

        # Добавление данных в базу
        phone = email_data.get('phone')
        if phone is not None:
            cursor.execute("INSERT INTO data (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            conn.commit()