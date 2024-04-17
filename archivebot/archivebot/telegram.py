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
import requests


class ExceptionTelegram(Exception):
    pass


class TelegramClient:
    """A Telegram Client"""

    @log.debug
    def __init__(self, token: str) -> None:
        """Init the client

        Parameters
        ----------
        token : str
            Token of the client
        update_offset : int
            First uptate to get
        update_timeout : int
            Timeout between calls
        """
        self._url = f"https://api.telegram.org/bot{token}"
        self._session = requests.Session()

    @log.debug
    def get_me(self) -> dict:
        """Get info about the client

        Returns
        -------
        dict
            Info about the client
        """
        return self._get("getMe")

    @log.debug
    def get_updates(self, offset, timeout) -> dict:
        """Get updates

        Returns
        -------
        dict
            Updates
        """
        params = {
            "offset": offset,
            "timeout": timeout
        }
        response = self._get("getUpdates", params)
        return response

    @log.debug
    def send_message(self, text: str, chat_id: int,
                     thread_id: int = 0) -> dict:
        """Send a message

        Parameters
        ----------
        text : str
            The message
        chat_id : int
            The chat_it
        thread_id : int
            The thread_id if any

        Returns
        -------
        dict
            The response
        """
        data = {
            "chat_id": chat_id,
            "text": text
        }
        if thread_id > 0:
            data.update({"message_thread_id": thread_id})
        return self._post("sendMessage", data)

    def get_member(self, chat_id, user_id):
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        return self._post("getChatMember", data)

    def get_administrators(self, chat_id):
        data = {
            "chat_id": chat_id
        }
        return self._post("getChatAdministrators", data)

    @log.debug
    def _get(self, endpoint: str, params: dict = {}) -> dict:
        """Send a generic GET

        Parameters
        ----------
        endpoint : str
            The endpoint
        params : dict
            Params for the query

        Returns
        -------
        dict
            Response from Telegram
        """
        url = f"{self._url}/{endpoint}"
        response = self._session.get(url, params=params)
        if response.status_code != 200:
            msg = f"Error HTTP {response.status_code}. {response.text}"
            raise ExceptionTelegram(msg)
        return response.json()

    @log.debug
    def _post(self, endpoint: str, data: dict = {}) -> dict:
        """Send a generic POST

        Parameters
        ----------
        endpoint : str
            The endpoint
        data : dict
            Data to send

        Returns
        -------
        dict
            Response from Telegram
        """
        url = f"{self._url}/{endpoint}"
        response = self._session.get(url, json=data)
        if response.status_code != 200:
            msg = f"Error HTTP {response.status_code}. {response.text}"
            raise ExceptionTelegram(msg)
        return response.json()
