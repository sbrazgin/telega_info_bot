#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  Sergey Brazgin 05/2019
  sbrazgin@mail.ru
  Project: Simple telegram bot for file messages
"""

import requests
import traceback
import json

from db_helper import DBHelper
from time import sleep


# ================================================
# == class BotHandler
# ================================================
# noinspection PyTypeChecker
class BotHandler:

    # -------------------------------------------------------------------------------
    def __init__(self, token, proxies, g_logger):
        self._token = token
        self._proxies = proxies
        self._g_logger = g_logger
        self._api_url = "https://api.telegram.org/bot{}/".format(self._token)
        self._shift_index_messages = 0

    # --public-----------------------------------------------------------------------------
    @property
    def shift_index_messages(self):
        return self._shift_index_messages

    # --public-----------------------------------------------------------------------------
    @shift_index_messages.setter
    def shift_index_messages(self, value):
        self._shift_index_messages = value

    # -------------------------------------------------------------------------------
    def get_updates(self, offset=None, timeout=10):
        method = 'getUpdates'
        params = {'timeout': timeout,
                  'offset': offset}
        try:
            resp = requests.get(self._api_url + method, params, proxies=self._proxies)
            self._g_logger.debug("resp" + str(resp))
            result_json = resp.json()['result']
        except Exception as e:
            self._g_logger.debug(e)
            traceback.print_exc()
            result_json = []

        return result_json

    # -------------------------------------------------------------------------------
    def send_message(self, chat_id, text):
        if '</' in text:
            return self.send_message_html(chat_id, text)
        else:
            params = {'chat_id': chat_id,
                      'text': text}
            method = 'sendMessage'
            resp = requests.post(self._api_url + method, params, proxies=self._proxies)
            return resp

    # -------------------------------------------------------------------------------
    def send_message_html(self, chat_id, text):
        params = {'chat_id': chat_id,
                  'text': text,
                  'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self._api_url + method, params, proxies=self._proxies)
        return resp

    # -------------------------------------------------------------------------------
    def get_last_update(self, offset=None, timeout=10):
        last_update = []

        get_result = self.get_updates(offset, timeout)

        self._g_logger.debug("get_result=" + str(get_result))
        if get_result:
            if len(get_result) > 0:
                last_update = get_result[-1]

        return last_update

    # -------------------------------------------------------------------------------
    def get_last_update_day(self, offset=None, timeout=1):
        get_results_day = self.get_updates(offset, timeout)

        self._g_logger.debug("get_results_day=" + str(get_results_day))
        return get_results_day

    # -------------------------------------------------------------------------------
    @staticmethod
    def build_keyboard(items):
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    # -------------------------------------------------------------------------------
    def send_message_list(self, chat_id, text, reply_markup):
        params = {'chat_id': chat_id,
                  'text': text,
                  'parse_mode': 'Markdown',
                  'reply_markup': reply_markup}
        method = 'sendMessage'
        resp = requests.post(self._api_url + method, params, proxies=self._proxies)
        return resp

    # -------------------------------------------------------------------------------
    def send_img_list(self, chat_id, img_file):
        self._g_logger.debug("send img=" + img_file)
        params = {'chat_id': chat_id
                  }
        # 'caption': 'Error'
        method = 'sendPhoto'
        files = {'photo': open(img_file, 'rb')}
        resp = requests.post(self._api_url + method, data=params, files=files,  proxies=self._proxies)
        return resp

    # -------------------------------------------------------------------------------
    def send_file_as_text(self, chat_id, file_data: str, file_name: str):
        if len(file_data) < 300:
            send_data = '<b>' + file_name + '</b> \n' + \
                        '------------------ \n' + \
                        file_data + '\n' + \
                        '------------------ '
        else:
            send_data = '<b>' + file_name + '</b> \n' + \
                        '------------------ \n' + \
                        file_data[:300] + '\n' + \
                        '<i> ... and others ... </i>' + \
                        '------------------ \n'

        resp = self.send_message(chat_id, send_data)
        return resp

    # -------------------------------------------------------------------------------
    def send_file_as_file(self, chat_id, file_name: str):
        params = {'chat_id': chat_id,
                  'caption': file_name
                  }
        method = 'sendDocument'
        files = {'document': open(file_name, 'rb')}
        resp = requests.post(self._api_url + method, data=params, files=files,  proxies=self._proxies)
        return resp

    # -------------------------------------------------------------------------------
    def shift_offset_to_new(self):
        # read all commands and forget it
        last_update = self.get_last_update()
        if last_update:
            last_update_id = last_update['update_id']
            new_offset = last_update_id + 1

            self._g_logger.debug('start: new_offset=' + str(new_offset))
            self.shift_index_messages = new_offset


# ================================================
# == class BotHandlerUsers (extends BotHandler)
# ================================================
class BotHandlerUsers(BotHandler):
    def __init__(self, token, proxies, g_logger, master_password):
        BotHandler.__init__(self, token, proxies, g_logger)
        self._db = DBHelper()
        self._master_password = master_password

    # -------------------------------------------------------------------------------
    def add_auth_user(self, chat_index, s_pass: str):
        self._g_logger.error('last_chat_id=' + str(chat_index) + ' try login: ' + s_pass + ' ...')
        if s_pass == self._master_password:
            self._g_logger.debug('last_chat_id=' + str(chat_index) + ' password OK, added to DB')
            self._db.add_item('OK', chat_index)
            self.send_message(chat_index, 'OK, pass checked')
        else:
            self._g_logger.error('last_chat_id=' + str(chat_index) + ' password error: '+s_pass)
            self.send_message(chat_index, 'Error, password incorrect !')

    # -------------------------------------------------------------------------------
    def check_auth_user(self, chat_index):
        count_rows = self._db.count_item('OK', chat_index)
        if count_rows > 0:
            return True
        else:
            return False

    # -------------------------------------------------------------------------------
    # send text message
    def send_message_to_all_auth_users(self, message: str):
        list_chats = self._db.get_chats('OK')
        for chat_index in list_chats:
            result = self.send_message(chat_index, message)
            self._g_logger.debug('result=' + str(result))
            self._g_logger.debug('result_text=' + str(result.text))

            result_json = json.loads(result.text)
            if not result_json['ok']:
                if 'chat not found' in result_json['description']:
                    self._g_logger.debug('delete from db chat=' + str(chat_index))
                    self._db.delete_item(chat_index)
            # The API will not allow more than ~30 messages to different users per second
            sleep(0.1)

    # -------------------------------------------------------------------------------
    # send file
    def send_file_to_all_auth_users(self, file_data: str, file_name: str):
        list_chats = self._db.get_chats('OK')
        for chat_index in list_chats:
            # send img
            if 'error' in file_name.lower():
                self.send_img_list(chat_index, 'lib/alert.png')

            # send text
            result = self.send_file_as_text(chat_index, file_data, file_name)

            # send text file
            if len(file_data) > 300:
                result = self.send_file_as_file(chat_index, file_name)

            self._g_logger.debug('result=' + str(result))
            self._g_logger.debug('result_text=' + str(result.text))

            result_json = json.loads(result.text)
            if not result_json['ok']:
                if 'chat not found' in result_json['description']:
                    self._g_logger.debug('delete from db chat=' + str(chat_index))
                    self._db.delete_item(chat_index)

            # The API will not allow more than ~30 messages to different users per second
            sleep(0.1)
