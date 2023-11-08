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
import time


def debug(func):
    logger = logging.getLogger(func.__module__)

    def wrap(*args, **kwargs):
        descriptor = f"{func.__module__}.{func.__name__}"
        logger.debug(f"Start: {descriptor}")
        if args:
            logger.debug(f"Args: {args}")
        if kwargs:
            logger.debug(f"Kwargs: {kwargs}")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        if result:
            logger.debug(f"Result: {result}")
        logger.debug(f"End: {descriptor} ({elapsed})")
        return result
    return wrap


def info(func):
    logger = logging.getLogger(func.__module__)

    def wrap(*args, **kwargs):
        descriptor = f"{func.__module__}.{func.__name__}"
        logger.info(f"start {descriptor}")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        logger.info(f"end {descriptor} ({elapsed})")
        return result
    return wrap


def warn(func):
    logger = logging.getLogger(func.__module__)

    def wrap(*args, **kwargs):
        descriptor = f"{func.__module__}.{func.__name__}"
        logger.warn(f"start {descriptor}")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        logger.warn(f"end {descriptor} ({elapsed})")
        return result
    return wrap


def error(func):
    logger = logging.getLogger(func.__module__)

    def wrap(*args, **kwargs):
        descriptor = f"{func.__module__}.{func.__name__}"
        logger.error(f"start {descriptor}")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        logger.error(f"end {descriptor} ({elapsed})")
        return result
    return wrap
