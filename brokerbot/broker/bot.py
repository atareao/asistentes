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

logger = logging.getLogger(__name__)

CURDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG = os.path.join(CURDIR, "config.json")


class BotException(Exception):
    pass


class Bot:
    def __init__(self, token, monitor, pool_time=300):
        logger.debug("__init__")
        self._pool_time = pool_time
        self._telegram_client = TelegramClient(token)
        self._monitor = monitor
        self._read_config()

    def _read_config(self) -> None:
        logger.debug("_read_config")
        if os.path.exists(CONFIG):
            with open(CONFIG, "r") as fr:
                config = json.load(fr)
                self._offset = config["offset"]
        else:
            self._offset = 0

    def _save_config(self) -> None:
        logger.debug("_save_config")
        with open(CONFIG, "w") as fw:
            config = {
                "offset": self._offset
            }
            json.dump(config, fw)

    def get_updates(self):
        logger.debug("get_updates")
        response = self._telegram_client.get_updates(self._offset,
                                                     self._pool_time)
        if response["ok"] and response["result"]:
            offset = max([item["update_id"] for item in response["result"]])
            self._offset = offset + 1
            self._save_config()
            self._process_response(response)

    def _process_response(self, response):
        logger.debug("_process_response")
        chat_id = None
        for message in response["result"]:
            try:
                logger.debug(f"Message: {message}")
                chat_id = message["message"]["chat"]["id"]
                if self._monitor.get_chat_id() is None:
                    self._monitor.set_chat_id(chat_id)
                text = message["message"]["text"]
                logger.debug(f"Text: {text}")
                if text.startswith("/help"):
                    self.process_help(message)
                elif text.startswith("/list"):
                    self.process_list(message)
                elif text.startswith("/get"):
                    self.process_get(message)
                elif text.startswith("/warning"):
                    self.process_warning(message)
                elif text.startswith("/max"):
                    self.process_max(message)
                elif text.startswith("/min"):
                    self.process_min(message)
                elif text.startswith("/configuration"):
                    self.process_configuration(message)
                elif text.startswith("/"):
                    command = text.split(" ")[0]
                    msg = f"The command {command} is not implemented"
                    raise BotException(msg)
            except Exception as exception:
                if chat_id:
                    self._telegram_client.send_message(str(exception), chat_id)

    def process_help(self, message):
        chat_id = message["message"]["chat"]["id"]
        items = []
        items.append("/help 👉 show this help")
        items.append("/list 👉 list Ibex 35 values")
        items.append("/get 👉 get a value (/get <action>)")
        items.append(
                "/max 👉 set max value for action (/max <action>,<value>)")
        items.append(
                "/min 👉 set min value for action (/min <action>,<value>)")
        items.append(
                "/configuration 👉 show max and min values configurated")
        self._telegram_client.send_message("\n".join(items), chat_id)

    def process_configuration(self, message):
        chat_id = message["message"]["chat"]["id"]
        data = self._monitor.get_data()
        if data:
            msg = "\n".join([f"{name} 👉 Max: {values['max']}, Min: {values['min']}" for name, values in data])
            self._telegram_client.send_message(msg, chat_id)
        else:
            msg = "There is no max and min values configurated"
            raise BotException(msg)



    def process_warning(self, message):
        logger.debug("process_warning")
        chat_id = message["message"]["chat"]["id"]
        self._monitor.set_chat_id(chat_id)

    def process_min(self, message):
        logger.debug("process_min")
        chat_id = message["message"]["chat"]["id"]
        text = message["message"]["text"]
        items = text.split(" ")
        if len(items) > 1 and items[1].find(",") > 0:
            name, value = items[1].split(",")
            value = float(value.strip())
            self._monitor.set_min(name, value)
            msg = f"Configured min value for {name} ({value})"
            self._telegram_client.send_message(msg, chat_id)
        else:
            msg = "Name and value are mandatories. Set as 'name,value'"
            raise BotException(msg)

    def process_max(self, message):
        logger.debug("process_max")
        chat_id = message["message"]["chat"]["id"]
        text = message["message"]["text"]
        items = text.split(" ")
        if len(items) > 1 and items[1].find(",") > 0:
            name, value = items[1].split(",")
            value = float(value.strip())
            self._monitor.set_max(name, value)
            msg = f"Configured max value for {name} ({value})"
            self._telegram_client.send_message(msg, chat_id)
        else:
            msg = "Name and value are mandatories. Set as 'name,value'"
            raise BotException(msg)

    def process_list(self, message):
        logger.debug("process_list")
        chat_id = message["message"]["chat"]["id"]
        response = ""
        data = self._monitor.get_current_data()
        logger.debug(f"Data: {data}")
        response = "\n".join([f"{name}: {value}"
                              for name, value in data.items()])
        self._telegram_client.send_message(response, chat_id=chat_id)

    def process_get(self, message):
        logger.debug("process_get")
        response = None
        text = message["message"]["text"]
        chat_id = message["message"]["chat"]["id"]
        items = text.split(" ")
        if len(items) > 1:
            name = items[1].title()
            data = self._monitor.get_current_data()
            if name in data.keys():
                response = f"Valor para {name}: {data[name]}"
            if response is None:
                msg = f"Error: no encontrado este valor para {name}"
                raise BotException(msg)
        else:
            msg = "Error: tienes que proporcionar un nombre"
            raise BotException(msg)
        self._telegram_client.send_message(response, chat_id=chat_id)
