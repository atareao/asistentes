#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2023 Lorenzo Carbonell <a.k.a. atareao>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import logging
import os
from telegram import TelegramClient
from expansion import Expansion

logger = logging.getLogger(__name__)

CURDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG = os.path.join(CURDIR, "config.json")


class ExceptionBot(Exception):
    pass


class Bot:
    def __init__(self, token, pool_time=300):
        self._pool_time = pool_time
        self._telegram_client = TelegramClient(token)
        self._read_config()

    def _read_config(self) -> None:
        if os.path.exists(CONFIG):
            with open(CONFIG, "r") as fr:
                config = json.load(fr)
                self._offset = config["offset"]
        else:
            self._offset = 0

    def _save_config(self) -> None:
        with open(CONFIG, "w") as fw:
            config = {
                "offset": self._offset
            }
            json.dump(config, fw)

    def get_updates(self):
        response = self._telegram_client.get_updates(self._offset,
                                                     self._pool_time)
        if response["ok"] and response["result"]:
            offset = max([item["update_id"] for item in response["result"]])
            self._offset = offset + 1
            self._save_config()
            self._process_response(response)

    def _process_response(self, response):
        for message in response["result"]:
            logger.debug(f"Message: {message}")
            text = message["message"]["text"]
            logger.debug(f"Text: {text}")
            if text == "/list":
                self.process_list(message)
            elif text.startswith("/get"):
                self.process_get(message)

    def process_list(self, message):
        chat_id = message["message"]["chat"]["id"]
        expansion = Expansion()
        response = ""
        values = expansion.get()
        logger.debug(f"Data: {values}")
        response = "\n".join([f"{item['name']}: {item['value']}"
                              for item in values])
        self._telegram_client.send_message(response, chat_id=chat_id)

    def process_get(self, message):
        response = None
        text = message["message"]["text"]
        chat_id = message["message"]["chat"]["id"]
        items = text.split(" ")
        if len(items) > 1:
            name = items[1]
            expansion = Expansion()
            values = expansion.get()
            for value in values:
                if name.lower() == value["name"].lower():
                    response = f"Valor para {name}: {value['value']}"
            if response is None:
                response = f"Error: no encontrado este valor para {name}"
        else:
            response = "Error: tienes que proporcionar un nombre"
        self._telegram_client.send_message(response, chat_id=chat_id)


