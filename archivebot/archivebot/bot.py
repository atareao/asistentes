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
from datetime import datetime


logger = logging.getLogger(__name__)

CURDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG = os.path.join(CURDIR, "config.json")
MAXDATE = datetime(2023, 12, 2, 23, 59, 59)
HAND = "👉"


class BotException(Exception):
    pass


class Bot:
    @log.debug
    def __init__(self, token, chat_id, thread_id, register: Register,
                 pool_time=300):
        self._pool_time = pool_time
        self._telegram_client = TelegramClient(token)
        self._chat_id = int(chat_id)
        self._thread_id = int(thread_id)
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
        thread_id = 0
        for message in response["result"]:
            try:
                chat_id = message["message"]["chat"]["id"]
                thread_id = message["message"]["message_thread_id"] if \
                    "message_thread_id" in message["message"] else 0
                if chat_id != self._chat_id or \
                        thread_id != self._thread_id or \
                        "text" not in message["message"]:
                    logger.debug(f"{chat_id} <=> {self._chat_id}")
                    logger.debug(f"{thread_id} <=> {self._thread_id}")
                    logger.debug("Me salgo")
                    return
                logger.debug(f"Message: {message}")
                text = message["message"]["text"]
                logger.debug(f"Text: {text}")
                if text.startswith("/help") or text.startswith("/ayuda"):
                    self.process_help(message)
                elif text.startswith("/participo"):
                    self.process_si(message)
                elif text.startswith("/noparticipo") or \
                        text.startswith("/no-participo"):
                    self.process_no(message)
                elif text.startswith("/estado"):
                    self.process_status(message)
                elif text.startswith("/sortea"):
                    self.process_sortea(message)
                elif text.startswith("/cuenta"):
                    self.process_count(message)
                elif text.startswith("/plazo"):
                    self.process_plazo(message)
                elif text.startswith("/"):
                    command = text.split(" ")[0]
                    msg = f"The command {command} is not implemented"
                    raise BotException(msg)
            except Exception as exception:
                if chat_id:
                    logger.error(exception)
                    self._telegram_client.send_message(str(exception), chat_id,
                                                       thread_id)

    @log.debug
    def process_help(self, message):
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        strbuf = StringIO()
        strbuf.write(f"`/ayuda` {HAND} muestra esta ayuda\n")
        strbuf.write(f"`/participo` {HAND} te añade a la lista del sorteo\n")
        strbuf.write(f"`/noparticipo` {HAND} te quita de la lista del "
                     "sorteo\n")
        strbuf.write(f"`/estado` {HAND} te indica si estás o no estás"
                     " registrado para el sorteo\n")
        strbuf.write(f"`/cuenta` {HAND} muestra el número de participantes\n")
        strbuf.write(f"`/plazo` {HAND} muestra el plazo del sorteo\n")
        strbuf.write(f"`/sortea` {HAND} realiza el sorteo\n")
        self._telegram_client.send_message(strbuf.getvalue(), chat_id,
                                           thread_id)

    @log.debug
    def process_si(self, message):
        user = message["message"]["from"]
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        username = user["username"] if "username" in user else None
        first_name = user["first_name"] if "first_name" in user else ""
        last_name = user["last_name"] if "last_name" in user else ""
        alias = f"@{username}" if username else f"{first_name} {last_name}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        elif datetime.now() > MAXDATE:
            message = f"`{alias}`, el plazo para apuntarse terminó. Lo siento."
        else:
            try:
                self._register.add(message["message"])
                message = f"Conseguido!, ya estás registrado `{alias}`"
            except RegisterExists:
                message = f"`{alias}`, ya estabas registrado para el sorteo!!"
            except Exception as exception:
                message = f"Error: {exception}"
        self._telegram_client.send_message(message, chat_id, thread_id)

    @log.debug
    def process_plazo(self, message):
        user = message["message"]["from"]
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        username = user["username"] if "username" in user else None
        first_name = user["first_name"] if "first_name" in user else ""
        last_name = user["last_name"] if "last_name" in user else ""
        alias = f"@{username}" if username else f"{first_name} {last_name}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        else:
            fechamax = MAXDATE.strftime("el %d/%m/%Y a las %H:%M:%S")
            message = f"`{alias}`, el plazo termina {fechamax}"
        self._telegram_client.send_message(message, chat_id, thread_id)

    @log.debug
    def process_no(self, message):
        user = message["message"]["from"]
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        username = user["username"] if "username" in user else None
        first_name = user["first_name"] if "first_name" in user else ""
        last_name = user["last_name"] if "last_name" in user else ""
        alias = f"@{username}" if username else f"{first_name} {last_name}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        elif datetime.now() > MAXDATE:
            message = f"`{alias}`, el plazo terminó. Lo siento."
        else:
            try:
                self._register.rm(message["message"])
                message = f"Vaya, lo siento!, ya no participas `{alias}`"
            except RegisterNotExists:
                message = f"`{alias}`, no estabas registrado para el sorteo!!"
            except Exception as exception:
                message = f"Error: {exception}"
        self._telegram_client.send_message(message, chat_id, thread_id)

    @log.debug
    def process_status(self, message):
        user = message["message"]["from"]
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        username = user["username"] if "username" in user else None
        first_name = user["first_name"] if "first_name" in user else ""
        last_name = user["last_name"] if "last_name" in user else ""
        alias = f"@{username}" if username else f"{first_name} {last_name}"
        if user["is_bot"]:
            message = f"`{alias}`, lo siento, los bot no pueden participar"
        else:
            try:
                if self._register.exists(message["message"]):
                    message = f"Estás registrado, `{alias}`"
                else:
                    message = f"NO estás registrado, `{alias}`"
            except RegisterNotExists:
                message = f"`{alias}`, no estabas registrado para el sorteo!!"
            except Exception as exception:
                message = f"Error: {exception}"
        self._telegram_client.send_message(message, chat_id, thread_id)

    @log.debug
    def process_count(self, message):
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        participantes = self._register.count()
        if participantes and participantes[0] > 0:
            message = f"Número de participantes: {participantes[0]}"
        else:
            message = "Todavía no hay ningún participante!!!"
        self._telegram_client.send_message(message, chat_id, thread_id)

    @log.debug
    def process_sortea(self, message):
        user = message["message"]["from"]
        chat_id = message["message"]["chat"]["id"]
        thread_id = message["message"]["message_thread_id"] if \
            "message_thread_id" in message["message"] else 0
        username = user["username"] if "username" in user else None
        first_name = user["first_name"] if "first_name" in user else ""
        last_name = user["last_name"] if "last_name" in user else ""
        alias = f"@{username}" if username else f"{first_name} {last_name}"
        response = self._telegram_client.get_administrators(chat_id)
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
            message = f"{alias}, solo los admin puendesortear! 😜"
        self._telegram_client.send_message(message, chat_id, thread_id)
