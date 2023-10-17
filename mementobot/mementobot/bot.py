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

from io import StringIO
import json
import logging
import os
from telegram import TelegramClient
from timewatcher import TimeWatcher

logger = logging.getLogger(__name__)

CURDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG = os.path.join(CURDIR, "config.json")
HAND = "👉"


class BotException(Exception):
    pass


class Bot:
    def __init__(self, token, time_watcher: TimeWatcher, pool_time=300):
        logger.debug("__init__")
        self._pool_time = pool_time
        self._telegram_client = TelegramClient(token)
        self._time_watcher = time_watcher
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
                if self._time_watcher.get_chat_id() is None:
                    self._time_watcher.set_chat_id(chat_id)
                text = message["message"]["text"]
                logger.debug(f"Text: {text}")
                if text.startswith("/help"):
                    self.process_help(message)
                elif text.startswith("/list"):
                    self.process_list(message)
                elif text.startswith("/add"):
                    self.process_add(message)
                elif text.startswith("/del"):
                    self.process_del(message)
                elif text.startswith("/"):
                    command = text.split(" ")[0]
                    msg = f"The command {command} is not implemented"
                    raise BotException(msg)
            except Exception as exception:
                if chat_id:
                    self._telegram_client.send_message(str(exception), chat_id)

    def process_help(self, message):
        chat_id = message["message"]["chat"]["id"]
        strbuf = StringIO()
        strbuf.write("/help show this help\n")
        strbuf.write("/list list all the reminders\n")
        strbuf.write("/add add a reminder (/set <when => message>)\n")
        strbuf.write("/del del a reminder (/del <index>)\n")
        self._telegram_client.send_message(strbuf.getvalue(), chat_id)

    def process_add(self, message):
        logger.debug("process_warning")
        data = message["message"]["text"][5:].strip().split("=>")
        logger.debug(data)
        when, msg = data
        self._time_watcher.add_reminder(when.strip(), msg.strip())

    def process_del(self, message):
        logger.debug("process_warning")
        index = message["message"]["text"][5:].strip()
        self._time_watcher.remove_reminder(index)

    def process_list(self, message):
        logger.debug("process_list")
        chat_id = message["message"]["chat"]["id"]
        response = ""
        data = self._time_watcher.get_reminders()
        if data:
            logger.debug(f"Data: {data}")
            response = "\n".join([f"{item['index']}. {item['when']} => \
                    {item['message']}" for item in data])
        else:
            response = "No reminders"
        self._telegram_client.send_message(response, chat_id=chat_id)
