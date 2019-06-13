'''
Sergey Brazgin    sbrazgin@gmail.com
Date 05/2019
Project: Simple telegram bot for file messages
'''

import sqlite3


class DBHelper:

    # -------------------------------------------------------------------------------
    def __init__(self, dbname="users.sqlite"):
        self._conn = sqlite3.connect(dbname)
        self._setup()

    # -------------------------------------------------------------------------------
    def _setup(self):
        print("creating table")
        stmt = "CREATE TABLE IF NOT EXISTS users (description text, owner text)"
        self._conn.execute(stmt)
        self._conn.commit()

    # -------------------------------------------------------------------------------
    def add_item(self, desc_text, owner):
        if self.count_item(desc_text, owner) == 0:
            stmt = "INSERT INTO users (description, owner) VALUES (?, ?)"
            args = (desc_text, owner)
            self._conn.execute(stmt, args)
            self._conn.commit()

    # -------------------------------------------------------------------------------
    def delete_item(self, owner):
        stmt = "DELETE FROM users WHERE owner = (?)"
        args = (owner, )
        self._conn.execute(stmt, args)
        self._conn.commit()

    # -------------------------------------------------------------------------------
    def get_items(self, owner):
        stmt = "SELECT description FROM users WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self._conn.execute(stmt, args)]

    # -------------------------------------------------------------------------------
    def get_chats(self, desc_text: str = 'OK'):
        stmt = "SELECT distinct owner FROM users WHERE description = (?)"
        args = (desc_text, )
        return [x[0] for x in self._conn.execute(stmt, args)]

    # -------------------------------------------------------------------------------
    def count_item(self, desc_text: str, owner: str) -> int:
        stmt = "select count(*) from users WHERE description = (?) and owner = (?)"
        cursor = self._conn.cursor()

        cursor.execute(stmt, (desc_text, owner))
        result = cursor.fetchone()
        number_of_rows = result[0]

        return int(number_of_rows)


