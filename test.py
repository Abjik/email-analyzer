import email
import re
import sqlite3
import email.parser

class EmailAnalyzer:
    def __init__(self, config):
        self.config = config

        self.mail_client = email.parser.Parser()

class EmailAnalyzer:
    def __init__(self, config):
        self.config = config

        self.mail_client = email.parser.Parser()
        self.db = sqlite3.connect(config["db_path"])

        self.trigger_recipients = config["trigger_recipients"]
        self.data_fields = config["data_fields"]

    def check_format(self, message):
        # Проверяем, что сообщение содержит все необходимые поля
        for field in self.data_fields:
            if field not in message.get_payload()[0].get_body():
                return False

        return True

    def extract_data(self, message):
        # Извлечем данные из сообщения
        data = {}
        for field in self.data_fields:
            match = re.search(f"{field}: (.*)", message.get_payload()[0].get_body())
            if match:
                data[field] = match.group(1)

        return data

    def insert_data(self, data):
        # Добавляем данные в базу данных
        cursor = self.db.cursor()
        cursor.execute(
            f"INSERT INTO data (name, email, phone) VALUES (?, ?, ?)",
            (data["name"], data["email"], data["phone"]),
        )
        self.db.commit()


def main():
    config = {
        "db_path": "/path/to/db.sqlite3",
        "trigger_recipients": ["example@example.com"],
        "data_fields": ["name", "email", "phone"],
    }

    analyzer = EmailAnalyzer(config)

    # TODO: получить сообщение из почтового ящика
    message = ...

    analyzer.analyze_message(message)


if __name__ == "__main__":
    main()
