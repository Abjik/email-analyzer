import imaplib
import email
import yaml
import sqlite3

# читаем конфиг файл
with open('config.yaml', 'r') as file:
    config = file.read()

my_config = yaml.load(config, Loader=yaml.FullLoader)
user, password = my_config['email_address'], my_config['password']
imap = my_config['imap_server']
message_format = my_config['message_format']

con = sqlite3.connect(my_config['db_path'])
cur = con.cursor()

# создаем таблицу
cur.execute("""CREATE TABLE IF NOT EXISTS data (
    name TEXT,
    email TEXT,
    messege TEXT
)""")

# подключаем IMAP сервер
my_mail = imaplib.IMAP4_SSL(imap)
my_mail.login(user, password)
my_mail.select('Inbox')

# получение данных
key = 'FROM'
values = my_config['trigger_recipients']

mail_id = []
for value in values:
    _, data = my_mail.search(None, f'{key} "{value}"')
    mail_id.extend(data[0].split())

msg = []
for num in mail_id:
    typ, data = my_mail.fetch(num, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_string(raw_email.decode("utf-8"))
    sender = email_message['From']
    subject = email_message['Subject']

    # работа с форматом
    message = [fmt.format(sender=sender, subject=subject) for fmt in message_format]

    # Получение тела сообщения
    if email_message.is_multipart():
        for part in email_message.get_payload():
            if part.get_content_type() == 'text/plain':
                message = part.get_payload(decode=True)
    else:
        message = email_message.get_payload(decode=True)

    # проверка наличия
    cur.execute("SELECT * FROM data WHERE email = ?", (sender,))
    if cur.fetchall() is not None:
        # добавление данных в базу данных
        cur.execute("INSERT INTO data (name, email, messege) VALUES (?, ?, ?)", (subject, sender, message))
        con.commit()

    msg.append(data)
