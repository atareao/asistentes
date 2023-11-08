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

import log
import logging
import sqlite3

"""
from': {'id': 3970104, 'is_bot': False, 'first_name': 'atareao', 'last_name': '🦀🐍🐋🦭🐧', 'username': 'atareao', 'language_code': 'es'}, 'chat': {'id': -1001923145772, 'title': 'atareao_curso', 'username': 'atareao_curso', 'type': 'supergroup'}, 'date': 1699419110, 'text': '/participo', 'entities': [{'offset': 0, 'length': 10, 'type': 'bot_command'}]}})
"""

PARTICIPANTES = """
    CREATE TABLE IF NOT EXISTS participantes(
        id INTEGER,
        is_bot BOOLEAN,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        language_code TEXT,
        chat_id INTEGER,
        timestamp INTEGER,
        premiado BOOLEAN
    )
"""

logger = logging.getLogger(__name__)


class RegisterException(Exception):
    pass


class RegisterExists(Exception):
    pass


class RegisterNotExists(Exception):
    pass


class Register:

    @log.debug
    def __init__(self, db):
        self._connection = sqlite3.connect(db)
        try:
            cursor = self._connection.cursor()
            cursor.execute(PARTICIPANTES)
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def list(self):
        try:
            sql = "SELECT * FROM participantes WHERE premiado = ?"
            data = (False,)
            cursor = self._connection.cursor()
            res = cursor.execute(sql, data)
            return res.fetchall()
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def set_premiado(self, id):
        try:
            sql = "UPDATE participantes SET premiado = ? WHERE id = ?"
            data = (True, id,)
            cursor = self._connection.cursor()
            result = cursor.execute(sql, data)
            self._connection.commit()
            return result
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def exists(self, message):
        try:
            user = message["from"]
            sql = "SELECT COUNT(*) FROM participantes WHERE id = ?"
            data = (user["id"],)
            cursor = self._connection.cursor()
            res = cursor.execute(sql, data)
            result = res.fetchone()
            return result is not None and result[0] > 0
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def add(self, message):
        user = message["from"]
        chat = message["chat"]
        timestamp = message["date"]
        if self.exists(message):
            raise RegisterExists("ya registrado")
        try:
            sql = ("INSERT INTO participantes (id, is_bot, first_name,"
                   " last_name, username, language_code, chat_id, timestamp,"
                   " premiado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
            data = (user["id"], user["is_bot"], user["first_name"],
                    user["last_name"], user["username"], user["language_code"],
                    chat["id"], timestamp, False,)
            logger.debug(data)
            cursor = self._connection.cursor()
            result = cursor.execute(sql, data)
            self._connection.commit()
            return result
        except Exception as e:
            logger.error(e)
            raise RegisterException(e)

    @log.debug
    def rm(self, message):
        user = message["from"]
        if not self.exists(message):
            raise RegisterNotExists("no registrado")
        try:
            sql = "DELETE FROM participantes WHERE id = ?"
            data = (user["id"],)
            cursor = self._connection.cursor()
            result = cursor.execute(sql, data)
            self._connection.commit()
            return result
        except Exception as e:
            logger.error(e)
            raise RegisterException(e)



