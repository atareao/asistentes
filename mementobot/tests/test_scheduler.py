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

import os
import sched
import time
from dotenv import load_dotenv
from mementobot.telegram import TelegramClient



class TestScheduler():

    @classmethod
    def setup_class(cls):
        load_dotenv()
        token = os.getenv("TOKEN", "")
        cls.chat_id = int(os.getenv("CHAT_ID", 0))
        cls.telegram_client = TelegramClient(token)
        cls.s = sched.scheduler(time.monotonic, time.sleep)

    def test_caso1(self):
        msg = "Primer caso"
        self.s.enter(10, 1, self.telegram_client.send_message,
                     argument=(msg, self.chat_id))
        self.s.run()
        data = 1
        assert data is not None
