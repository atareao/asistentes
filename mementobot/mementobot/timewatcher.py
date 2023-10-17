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

import logging
from dateparser import parse
from datetime import datetime
from telegram import TelegramClient
from threading import Thread
from time import sleep
from typing import Optional

SETTINGS = {"DEFAULT_LANGUAGES": ["es"],
            "TIMEZONE": "UTC"}
SLEEP_TIME = 1

logger = logging.getLogger(__name__)


class TimeWatcherException(Exception):
    pass


class TimeWatcher(Thread):
    def __init__(self, token: str) -> None:
        logger.debug("__init__")
        super().__init__()
        self.setDaemon(True)
        self._telegram_client = TelegramClient(token)
        self._chat_id = None
        self._reminders = []

    def set_chat_id(self, chat_id: int) -> None:
        logger.debug("set_chat_id")
        self._chat_id = chat_id

    def get_chat_id(self) -> Optional[int]:
        logger.debug("get_chat_id")
        return self._chat_id

    def get_max(self) -> int:
        logger.debug("get_max")
        max = 0
        for reminder in self._reminders:
            if reminder["index"] > max:
                max = reminder["index"]
        return max

    def get_reminders(self):
        return self._reminders

    def add_reminder(self, when, message) -> None:
        logger.debug("add_reminder")
        index = self.get_max()
        try:
            timestamp = parse(when, settings=SETTINGS).timestamp()
            self._reminders.append({"index": index, "when": when,
                                    "timestamp": timestamp,
                                    "message": message})
        except Exception as exception:
            raise TimeWatcherException(exception)

    def remove_reminder(self, index):
        logger.debug("remove_reminder")
        for reminder in self._reminders:
            if reminder["index"] == index:
                logger.debug(f"delete reminder: {index}")
                del self._reminders[index]
                return
        raise TimeWatcherException("Reminder not found")

    def run(self):
        while True:
            for reminder in self._reminders:
                now = datetime.now().timestamp()
                logger.debug(f"{reminder['index']} - {now} > {reminder['timestamp']}")
                if now > reminder["timestamp"]:
                    logger.debug(f"Send reminder: {reminder['index']}")
                    if self._chat_id is not None:
                        self._telegram_client.send_message(reminder["message"],
                                                           self._chat_id)
                        self.remove_reminder(reminder["index"])
                    else:
                        raise TimeWatcherException("Chat id not set")
            sleep(SLEEP_TIME)
