#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  Sergey Brazgin 05/2019
  sbrazgin@mail.ru
  Project: Simple telegram bot for file messages
"""

from file_db_services import FileDbHelper
from bot_helper import BotHandlerUsers
import time
import configparser
import logging
import logging.config
import datetime


# -- MAIN -----------------------------------------------------------
def main():
    # -- init params --------------------------------
    def load_init_params():
        global g_token
        global g_report_dir
        global g_report_drop_dir
        global g_proxies
        global g_password

        # read input params
        config = configparser.ConfigParser()
        config.read('config.ini')

        g_token = config['CHAT']['chat_token']
        g_report_dir = config['REPORTS']['report_dir']
        g_report_drop_dir = config['REPORTS']['report_drop_dir']

        g_proxy_1 = config['INET_PROXY']['http_proxy']
        g_proxy_2 = config['INET_PROXY']['https_proxy']
        g_proxies = {
            'http': g_proxy_1,
            'https': g_proxy_2
        }

        g_password = config['CHAT']['chat_pass']

        g_logger.debug('--- read config params: ---')
        g_logger.debug('g_report_dir=' + g_report_dir)
        g_logger.debug('g_report_drop_dir=' + g_report_drop_dir)
        g_logger.debug('g_proxy_1=' + g_proxy_1)
        g_logger.debug('g_proxy_2=' + g_proxy_2)
        g_logger.debug('g_password=' + g_password)
        g_logger.debug('--- End read ---')

    # ---------------------------------------------
    def check_input_files():
        list_info_file = cl_file_db_helper.get_files()
        g_logger.debug('list files=' + str(list_info_file))

        for c_file_name in list_info_file:
            c_file_data = cl_file_db_helper.get_file_cont(c_file_name)
            g_logger.debug('c_file_data from ' + c_file_name + ' = ' + str(c_file_data))
            cl_bot_handler.send_file_to_all_auth_users(c_file_data, g_report_dir + c_file_name)

            cl_file_db_helper.drop_file(c_file_name)

    # ---------------------------------------------
    def check_input_message(last_update):

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        g_logger.debug("last_update_id=" + str(last_update_id))
        g_logger.debug("last_chat_text=" + str(last_chat_text))
        g_logger.debug("last_chat_id=" + str(last_chat_id))
        g_logger.debug("last_chat_name=" + str(last_chat_name))

        t = last_chat_text.lower()
        # === INPUT MESSAGE = HELLO
        if t in ('здравствуй', 'привет', 'ку', 'здорово'):
            now = datetime.datetime.now()
            today = now.day
            hour = now.hour
            if today == now.day and 6 <= hour < 12:
                cl_bot_handler.send_message(last_chat_id, 'Доброе утро, {}'.format(last_chat_name))

            if today == now.day and 12 <= hour < 17:
                cl_bot_handler.send_message(last_chat_id, 'Добрый день, {}'.format(last_chat_name))

            if today == now.day and 17 <= hour < 23:
                cl_bot_handler.send_message(last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))

        # === INPUT MESSAGE = help
        elif t == '/help':
            cl_bot_handler.send_message(last_chat_id, '/help - help\n' +
                                        '/login [pass] - login\n' +
                                        '/list - list all monitoring db\n'
                                        '/check [db_name]- check status db\n')

        # === INPUT MESSAGE = login
        elif t.startswith('/login'):
            args = last_chat_text.split(" ")
            s_pass = ''
            if len(args) > 1:
                s_pass = args[1]
            cl_bot_handler.add_auth_user(last_chat_id, s_pass)

        # === INPUT MESSAGE = check
        elif t.startswith('/check'):
            args = last_chat_text.split(" ")
            s_db = ''
            if len(args) > 1:
                s_db = args[1]

            if cl_bot_handler.check_auth_user(last_chat_id):
                cl_bot_handler.send_message(last_chat_id, 'OK {} Status = {}'.format(s_db, 'OK'))
            else:
                cl_bot_handler.send_message(last_chat_id, 'Error, please login')

        # === INPUT MESSAGE = test
        elif t.startswith('/test_buttons'):
            build_keyboard = cl_bot_handler.build_keyboard(['qwe1', 'asd1', 'zxc', 'zxc_TTT'])
            cl_bot_handler.send_message_list(last_chat_id, 'Выбери 1', build_keyboard)

        elif t.startswith('/test_img'):
            cl_bot_handler.send_img_list(last_chat_id, 'lib/alert.png')

        else:
            g_logger.error('last_chat_id=' + str(last_chat_id) + ' error command: ' + t)

        cl_bot_handler.shift_index_messages = last_update_id + 1

    # ------------------------------------------------------------

    # -- MAIN -------------------------------------------
    # create logger
    logging.config.fileConfig('logging.conf')
    g_logger = logging.getLogger()
    g_logger.info('Started')

    # -- init params
    load_init_params()

    # create service classes
    cl_bot_handler = BotHandlerUsers(g_token, g_proxies, g_logger, g_password)
    cl_bot_handler.shift_offset_to_new()
    cl_bot_handler.send_message_to_all_auth_users('Hello all DBAs !')

    cl_file_db_helper = FileDbHelper(g_report_dir, g_report_drop_dir, g_logger)

    # --- main loop -----------
    while True:
        last_updates = cl_bot_handler.get_last_update_day(cl_bot_handler.shift_index_messages)
        if last_updates:
            # check and run all user commands
            for c_update in last_updates:
                check_input_message(c_update)

        # check and send all files
        check_input_files()

        time.sleep(5)


# -------------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
