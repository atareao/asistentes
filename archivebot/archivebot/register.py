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

CONVERSATIONS = """
    CREATE TABLE IF NOT EXISTS conversations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT "",
        description TEXT DEFAULT "",
        filename TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAM
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
            cursor.execute(CONVERSATIONS)
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def list(self):
        try:
            sql = "SELECT * FROM consersations"
            cursor = self._connection.cursor()
            res = cursor.execute(sql)
            return res.fetchall()
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def count(self):
        try:
            sql = "SELECT count(1) FROM conversations"
            cursor = self._connection.cursor()
            res = cursor.execute(sql)
            return res.fetchone()
        except Exception as e:
            raise RegisterException(e)

    @log.debug
    def add_filename(self, filename):
        try:
            sql = "INSERT INTO consersations (filename) VALUES (?)"
            data = (filename,)
            cursor = self._connection.cursor()
            result = cursor.execute(sql, data)
            self._connection.commit()
            return result
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
            username = user["username"] if "username" in user else ""
            first_name = user["first_name"] if "first_name" in user else ""
            last_name = user["last_name"] if "last_name" in user else ""
            language_code = user["language_code"] if "language_code" in user \
                else ""
            data = (user["id"], user["is_bot"], first_name, last_name,
                    username, language_code, chat["id"], timestamp, False,)
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
