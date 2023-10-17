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

from dateparser import parse

SETTINGS = {"DEFAULT_LANGUAGES": ["es"],
            "TIMEZONE": "Europe/Madrid"}


class TestDateParser():

    def test_caso1(self):
        data = parse("dentro de 10 segundos", settings=SETTINGS)
        print(data)
        assert data is not None

    def test_caso2(self):
        data = parse("en 10 segundos", settings=SETTINGS)
        print(data)
        assert data is not None

    def test_caso3(self):
        data = parse("dentro de 2 horas", settings=SETTINGS)
        print(data)
        assert data is not None

    def test_caso4(self):
        data = parse("mañana a las 12:45", settings=SETTINGS)
        print(data)
        assert data is not None

    def test_caso5(self):
        data = parse("12 de diciembre a las 14:35", settings=SETTINGS)
        print(data)
        assert data is not None
