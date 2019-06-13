'''
Sergey Brazgin    sbrazgin@gmail.com
Date 05/2019
Project: Simple telegram bot for file messages
'''

from db_helper import DBHelper
import datetime
import json
from time import sleep


class BotAdminCommands:

    # -------------------------------------------------------------------------------
    def __init__(self, greet_bot, g_logger, master_password):
        # private
        self._bot_handler = greet_bot
        self._db = DBHelper()
        self.g_logger = g_logger
        self._master_password = master_password

        # public
        self.shift_index_messages = 0

    # -------------------------------------------------------------------------------
    def send_to_all_auth_users(self, message: str):
        list_chats = self._db.get_chats('OK')
        for chat_index in list_chats:
            result = self._bot_handler.send_message(chat_index, message)
            self.g_logger.debug('result=' + str(result))
            self.g_logger.debug('result_text=' + str(result.text))

            result_json = json.loads(result.text)
            if not result_json['ok']:
                if 'chat not found' in result_json['description']:
                    self.g_logger.debug('delete from db chat=' + str(chat_index))
                    self._db.delete_item(chat_index)
            # The API will not allow more than ~30 messages to different users per second
            sleep(0.1)


    # -------------------------------------------------------------------------------
    def check_one_row(self, last_update):

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        self.g_logger.debug("last_update_id=" + str(last_update_id))
        self.g_logger.debug("last_chat_text=" + str(last_chat_text))
        self.g_logger.debug("last_chat_id=" + str(last_chat_id))
        self.g_logger.debug("last_chat_name=" + str(last_chat_name))

        t =last_chat_text.lower()
        # === INPUT MESSAGE = HELLO
        if t in ('здравствуй', 'привет', 'ку', 'здорово'):
            now = datetime.datetime.now()
            today = now.day
            hour = now.hour
            if today == now.day and 6 <= hour < 12:
                self._bot_handler.send_message(last_chat_id, 'Доброе утро, {}'.format(last_chat_name))

            if today == now.day and 12 <= hour < 17:
                self._bot_handler.send_message(last_chat_id, 'Добрый день, {}'.format(last_chat_name))

            if today == now.day and 17 <= hour < 23:
                self._bot_handler.send_message(last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))


        # === INPUT MESSAGE = help
        if t == '/help':
            self._bot_handler.send_message(last_chat_id, '/help - help\n' +
                                   '/login [pass] - login\n' +
                                   '/list - list all monitoring db\n'
                                   '/check [db_name]- check status db\n')

        # === INPUT MESSAGE = login
        if t.startswith('/login'):
            args = last_chat_text.split(" ")
            s_pass = ''
            if len(args) > 1:
                s_pass = args[1]
            self.g_logger.debug('/login: s_pass=' + s_pass)
            if s_pass == self._master_password:
                self.g_logger.debug('last_chat_id=' + last_chat_id + 'added to DB')
                self._db.add_item('OK', last_chat_id)
                self._bot_handler.send_message(last_chat_id, 'OK, pass checked')

        # === INPUT MESSAGE = check
        if t.startswith('/check'):
            args = last_chat_text.split(" ")
            s_db = ''
            if len(args) > 1:
                s_db = args[1]

            count_rows = self._db.count_item('OK', last_chat_id)
            self.g_logger.debug('last_chat_id=' + str(last_chat_id) + 'count_rows=' + str(count_rows))

            if count_rows>0:
                self._bot_handler.send_message(last_chat_id, 'OK {} Status = {}'.format(s_db, 'OK'))
            else:
                self._bot_handler.send_message(last_chat_id, 'Error, please login')

        # === INPUT MESSAGE = test
        if t.startswith('/test'):
            build_keyboard = self._bot_handler.build_keyboard(['qwe1', 'asd1', 'zxc', 'zxc_TTT'])
            self._bot_handler.send_message_2(last_chat_id, 'Выбери 1', build_keyboard)

        self.shift_index_messages = last_update_id + 1
    # ------------------------------------------------------------


