import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import json
import sqlite3
import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

mail = imaplib.IMAP4_SSL(config['imap_server'])
mail.login(config['email_address'], config['password'])
mail.select("inbox")

result, data = mail.uid('search', None, "ALL")

email_ids = data[0].split()

conn = sqlite3.connect(config['db_path'])
cursor = conn.cursor()

for id in email_ids:
    result, message_data = mail.uid('fetch', id, '(BODY.PEEK[])')
    raw_email = message_data[0][1].decode("utf-8")
    email_message = email.message_from_string(raw_email)
    from_ = email.utils.parseaddr(email_message['From'])[1]
    if from_ not in config['trigger_recipients']:
        continue

    email_data = {}
    if email_message.is_multipart():
        for payload in email_message.get_payload():
            body = payload.get_payload(decode=True)
            try:
                email_data = json.loads(body)
            except json.JSONDecodeError:
                continue
    else:
        body = email_message.get_payload(decode=True)
        try:
            email_data = json.loads(body)
        except json.JSONDecodeError:
            continue

    cursor.execute("SELECT * FROM data WHERE name = ? AND email = ?", (email_data.get('name'), email_data.get('email')))
    if cursor.fetchone() is None:
        continue

    cursor.execute("INSERT INTO data (name, email, phone) VALUES (?, ?, ?)", (email_data.get('name'), email_data.get('email'), email_data.get('phone')))
    conn.commit()

conn.close()