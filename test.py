import imaplib
import email
import json
import sqlite3

imap_server = "imap.gmail.com"
email_address = "200107009@stu.sdu.edu.kz"
password = "abzhiknotgay"

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_address, password)

imap.select("Inbox")

_, msgnums = imap.search(None, "ALL")

# список адресатов
senders = ["sender1@gmail.com", "sender2@gmail.com"]

# подключение к базе данных
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

for msgnum in msgnums[0].split():
    _, data = imap.fetch(msgnum, "(BODY[])")
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    # проверка отправителя
    from_ = email.utils.parseaddr(email_message['From'])[1]
    if from_ not in senders:
        continue

    # проверка формата сообщения
    if email_message.is_multipart():
        for payload in email_message.get_payload():
            body = payload.get_payload(decode=True)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                continue
    else:
        body = email_message.get_payload(decode=True)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            continue

    # проверка данных из сообщения с данными из базы данных
    cursor.execute("SELECT * FROM my_table WHERE field1 = ? AND field2 = ?", (data['field1'], data['field2']))
    if cursor.fetchone() is None:
        continue

    # добавление новой строки в базу данных
    cursor.execute("INSERT INTO my_table (field3, field4, field5) VALUES (?, ?, ?)", (data['field3'], data['field4'], data['field5']))
    conn.commit()

conn.close()