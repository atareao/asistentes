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

import lxml.html
import requests


class IbexException(Exception):
    pass


class Ibex:
    """
    Obtiene los datos del Ibex 35
    Url: https://bolsarama.es/acciones/ibex35

    Attributes
    ----------
    headers : Encabezados
    """
    url = "https://bolsarama.es/acciones/ibex35"

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X "
                           "10_10_1) AppleWebKit/537.36 (KHTML, "
                           "like Gecko) Chrome/39.0.2171.95 "
                           "Safari/537.36")}

    def get(self):
        response = self._session.get(Ibex.url)
        if response.status_code != 200:
            msg = f"HTTP Error: {response.status_code}. {response.text}"
            raise IbexException(msg)
        return self.process(response.text)

    @staticmethod
    def process(content):
        data = {}
        root = lxml.html.fromstring(content)
        rows = root.cssselect("table.table.table-responsive>tbody>tr")
        for row in rows:
            th = row.cssselect("th>a")[0]
            name = th.text
            td = row.cssselect("td>span")[0]
            price = td.text
            data[name] = price
        return data
