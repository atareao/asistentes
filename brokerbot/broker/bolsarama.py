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
import lxml.html
import requests

logger = logging.getLogger(__name__)


class BolsaramaException(Exception):
    pass


class Bolsarama:
    """
    Obtiene los datos del Ibex 35
    Url: https://bolsarama.es/acciones/ibex35

    Attributes
    ----------
    headers : Encabezados
    """
    url = "https://bolsarama.es/acciones/ibex35"

    def __init__(self) -> None:
        logger.debug("__init__")
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X "
                           "10_10_1) AppleWebKit/537.36 (KHTML, "
                           "like Gecko) Chrome/39.0.2171.95 "
                           "Safari/537.36")}

    def get(self):
        logger.debug("get")
        response = self._session.get(self.url)
        logger.debug(f"Response. Status code: {response.status_code}. Content:"
                     f"response.text")
        if response.status_code != 200:
            msg = f"HTTP Error: {response.status_code}. {response.text}"
            raise BolsaramaException(msg)
        return self.process(response.text)

    @staticmethod
    def process(content):
        logger.debug("process")
        data = {}
        root = lxml.html.fromstring(content)
        rows = root.cssselect("table.table.table-responsive>tbody>tr")
        for row in rows:
            th = row.cssselect("th>a")[0]
            name = th.text.title()
            td = row.cssselect("td>span")[0]
            price = float(td.text[:-1].replace(",", "."))
            data[name] = price
        return data
