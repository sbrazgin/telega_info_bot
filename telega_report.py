'''
Sergey Brazgin    sbrazgin@gmail.com
Date 05/2019
Project: Simple telegram bot for file messages
'''


#!/usr/bin/env python3
from bot_helper import BotHandler
from bot_admin import BotAdminCommands
from file_db_services import File_DB_helper
import time
import configparser
import logging
import logging.config


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

    # -- MAIN -------------------------------------------
    # create logger
    logging.config.fileConfig('logging.conf')
    g_logger = logging.getLogger()
    g_logger.info('Started')

    # -- init params
    load_init_params()

    new_offset = None

    # create service classes
    bot_handler = BotHandler(g_token, g_proxies, g_logger)
    bot_admin = BotAdminCommands(bot_handler, g_logger, g_password)
    file_db_helper = File_DB_helper(g_report_dir, g_report_drop_dir)

    last_update = bot_handler.get_last_update()
    if last_update:
        last_update_id = last_update['update_id']
        new_offset = last_update_id + 1

    g_logger.debug('start: new_offset=' + str(new_offset))
    bot_admin.shift_index_messages = new_offset

    while True:
        last_updates = bot_handler.get_last_update_day(bot_admin.shift_index_messages)
        if last_updates:
            for c_update in last_updates:
                bot_admin.check_one_row(c_update)

        list_info_file =file_db_helper.get_files()
        g_logger.debug('list files=' + str(list_info_file))
        for c_file_name in list_info_file:
            c_file_data = file_db_helper.get_file_cont(c_file_name)
            g_logger.debug('c_file_data=' + str(c_file_data))
            if len(c_file_data) < 300:
                send_data = c_file_data
                bot_admin.send_to_all_auth_users(send_data)
                file_db_helper.drop_file(c_file_name)

        time.sleep(5)
# -------------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

