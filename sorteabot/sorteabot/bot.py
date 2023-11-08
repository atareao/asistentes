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
import log
import os
import random
from telegram import TelegramClient
from register import Register, RegisterExists, RegisterNotExists


logger = logging.getLogger(__name__)

CURDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG = os.path.join(CURDIR, "config.json")
HAND = "👉"


class BotException(Exception):
    pass


class Bot:
    @log.debug
    def __init__(self, token, register: Register, pool_time=300):
        self._pool_time = pool_time
        self._telegram_client = TelegramClient(token)
        self._register = register
        self._read_config()

    @log.debug
    def _read_config(self) -> None:
        if os.path.exists(CONFIG):
            with open(CONFIG, "r") as fr:
                config = json.load(fr)
                self._offset = config["offset"]
        else:
            self._offset = 0

    @log.debug
    def _save_config(self) -> None:
        with open(CONFIG, "w") as fw:
            config = {
                "offset": self._offset
            }
            json.dump(config, fw)

    @log.debug
    def get_updates(self):
        response = self._telegram_client.get_updates(self._offset,
                                                     self._pool_time)
        if response["ok"] and response["result"]:
            offset = max([item["update_id"] for item in response["result"]])
            self._offset = offset + 1
            self._save_config()
            self._process_response(response)

    @log.debug
    def _process_response(self, response):
        chat_id = None
        for message in response["result"]:
            try:
                logger.debug(f"Message: {message}")
                chat_id = message["message"]["chat"]["id"]
                text = message["message"]["text"]
                logger.debug(f"Text: {text}")
                if text.startswith("/help") or text.startswith("/ayuda"):
                    self.process_help(message)
                elif text.startswith("/participo"):
                    self.process_si(message)
                elif text.startswith("/no-participo"):
                    self.process_no(message)
                elif text.startswith("/sortea"):
                    self.process_sortea(message)
                elif text.startswith("/"):
                    command = text.split(" ")[0]
                    msg = f"The command {command} is not implemented"
                    raise BotException(msg)
            except Exception as exception:
                if chat_id:
                    self._telegram_client.send_message(str(exception), chat_id)

    @log.debug
    def process_help(self, message):
        chat_id = message["message"]["chat"]["id"]
        strbuf = StringIO()
        strbuf.write(f"`/ayuda` {HAND} muestra esta ayuda\n")
        strbuf.write(f"`/participo` {HAND} te añade a la lista del sorteo\n")
        strbuf.write(f"`/no-participo` {HAND} te quita de la lista del "
                     "sorteo\n")
        strbuf.write(f"`/sortea` {HAND} realiza el sorteo\n")
        self._telegram_client.send_message(strbuf.getvalue(), chat_id)

    @log.debug
    def process_si(self, message):
        user = message["message"]["from"]
        chat = message["message"]["chat"]
        alias = f"@{user['username']}" if user["username"] \
                else f"{user['first_name']} {user['last_name']}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        else:
            try:
                self._register.add(message["message"])
                message = f"Conseguido!, ya estás registrado `{alias}`"
            except RegisterExists:
                message = f"`{alias}`, ya estabas registrado para el sorteo!!"
            except Exception as exception:
                message = str(exception)
        self._telegram_client.send_message(message, chat["id"])

    @log.debug
    def process_no(self, message):
        user = message["message"]["from"]
        chat = message["message"]["chat"]
        alias = f"@{user['username']}" if user["username"] \
                else f"{user['first_name']} {user['last_name']}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        else:
            try:
                self._register.rm(message["message"])
                message = f"Vaya, lo siento!, ya no participas `{alias}`"
            except RegisterNotExists:
                message = f"`{alias}`, no estabas registrado para el sorteo!!"
            except Exception as exception:
                message = str(exception)
        self._telegram_client.send_message(message, chat["id"])

    @log.debug
    def process_sortea(self, message):
        chat = message["message"]["chat"]
        user = message["message"]["from"]
        alias = f"@{user['username']}" if user["username"] \
                else f"{user['first_name']} {user['last_name']}"
        response = self._telegram_client.get_administrators(chat["id"])
        admin_ids = [user["user"]["id"] for user in response["result"]]
        logger.debug(admin_ids)
        if user["id"] in admin_ids:
            participantes = self._register.list()
            logger.debug(f"Participantes: {participantes}")
            selected = int(random.uniform(0, len(participantes)))
            seleccionado = participantes[selected]
            logger.debug(f"Seleccionado: {selected}")
            logger.debug(f"Seleccionado: {seleccionado}")
            message = f"El premiado es {seleccionado}"
        else:
            message = f"`{alias}`, solo los administradores pueden sortear!!!"
        self._telegram_client.send_message(message, chat["id"])


