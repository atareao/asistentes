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
from expansion import Expansion
from telegram import TelegramClient
from threading import Thread
from time import sleep

logger = logging.getLogger(__name__)
TIME_LAPSE = 300


class MonitorException(Exception):
    pass


class Monitor(Thread):
    def __init__(self, token: str) -> None:
        logger.debug("__init__")
        super().__init__()
        self._daemon = True
        self._telegram_client = TelegramClient(token)
        self._expansion = Expansion()
        self._initial_data = self._expansion.get()
        self._current_data = self._initial_data
        self._data = {}
        self._increment = 100
        self._decrement = 100
        self._chat_id = None

    def set_chat_id(self, chat_id):
        logger.debug("set_chat_id")
        self._chat_id = chat_id

    def get_chat_id(self):
        return self._chat_id

    def set_increment(self, increment):
        logger.debug("set_increment")
        if increment < 0:
            msg = f"{increment} is not a valid value"
            raise MonitorException(msg)
        self._increment = increment

    def set_max(self, name, value):
        logger.debug("set_max")
        if name not in self._current_data:
            msg = f"{name} is not in Ibex 35"
            raise MonitorException(msg)
        if name in self._data:
            self._data[name]["max"] = value
            self._data[name]["maxw"] = False
        else:
            self._data[name] = {"max": value, "min": None, "maxw": False,
                                "minw": False}
        logger.debug(self._data)

    def set_min(self, name, value):
        logger.debug("set_min")
        if name not in self._current_data:
            msg = f"{name} is not in Ibex 35"
            raise MonitorException(msg)
        if name in self._data:
            self._data[name]["max"] = value
            self._data[name]["maxw"] = False
        else:
            self._data[name] = {"max": value, "min": None, "maxw": False,
                                "minw": False}
        logger.debug(self._data)

    def set_decrement(self, decrement):
        logger.debug("set_decrement")
        if decrement < 0:
            msg = f"{decrement} is not a valid value"
            raise MonitorException(msg)
        self._decrement = decrement

    def get_current_data(self):
        logger.debug("get_current_data")
        return self._current_data

    def run(self):
        logger.debug("run")
        while True:
            self.current_data = self._expansion.get()
            if self._chat_id is not None:
                logger.debug("== check ==")
                logger.debug(self._current_data)
                logger.debug(self._data)
                variations = []
                for name, current_value in self._current_data.items():
                    initial_value = self._initial_data[name]
                    variation = (current_value - initial_value)/initial_value
                    if variation > 0 and variation > self._increment:
                        # send message
                        msg = f"El valor de {name} se incremento {variation}%"
                        variations.append(msg)
                    elif variation < 0 and abs(variation) > self._decrement:
                        # send message
                        msg = f"El valor de {name} se decrementó {variation}%"
                        variations.append(msg)
                    if name in self._data:
                        if self._data[name]["min"] is not None and \
                                self._data[name]["min"] > current_value and \
                                self._data[name]["minw"] is False:
                            msg = (f"El valor de {name} bajó por debajo de el "
                                   "mínimo fijado")
                            self._data[name]["minw"] = True
                            variations.append(msg)
                        if self._data[name]["max"] is not None and \
                                self._data[name]["max"] < current_value and \
                                self._data[name]["maxw"] is False:
                            msg = f"El valor de {name} superó el máximo fijado"
                            self._data[name]["maxw"] = True
                            variations.append(msg)

                if variations:
                    msg = "\n".join(variations)
                    self._telegram_client.send_message(msg, self._chat_id)
            sleep(TIME_LAPSE)
