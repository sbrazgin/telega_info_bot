'''
Sergey Brazgin    sbrazgin@gmail.com
Date 05/2019
Project: Simple telegram bot for file messages
'''

import requests
import traceback
import json


class BotHandler:

    # -------------------------------------------------------------------------------
    def __init__(self, token, proxies, g_logger):
        self.token = token
        self.proxies = proxies
        self.g_logger = g_logger
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)

    # -------------------------------------------------------------------------------
    def get_updates(self, offset=None, timeout=10):
        method = 'getUpdates'
        params = {'timeout': timeout,
                  'offset': offset}
        try:
            resp = requests.get(self.api_url + method, params, proxies=self.proxies)
            self.g_logger.debug("resp" + str(resp))
            result_json = resp.json()['result']
        except Exception as e:
            self.g_logger.debug(e)
            traceback.print_exc()
            result_json = []

        return result_json

    # -------------------------------------------------------------------------------
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id,
                  'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params, proxies=self.proxies)
        return resp

    # -------------------------------------------------------------------------------
    def get_last_update(self, offset=None, timeout=10):
        last_update = []

        get_result = self.get_updates(offset,timeout)

        self.g_logger.debug("get_result=" + str(get_result))
        if get_result:
            if len(get_result) > 0:
                last_update = get_result[-1]

        return last_update

    # -------------------------------------------------------------------------------
    def get_last_update_day(self, offset=None, timeout=1):
        get_results_day = self.get_updates(offset, timeout)

        self.g_logger.debug("get_results_day=" + str(get_results_day))
        return get_results_day

    # -------------------------------------------------------------------------------
    def build_keyboard(self, items):
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    # -------------------------------------------------------------------------------
    def send_message_2(self, chat_id, text,reply_markup):
        params = {'chat_id': chat_id,
                  'text': text,
                  'parse_mode': 'Markdown',
                  'reply_markup':reply_markup}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params, proxies=self.proxies)
        return resp


