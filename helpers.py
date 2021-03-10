#!/usr/bin/env python3

from pathlib import Path
import datetime
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)
base_path = os.path.dirname(__file__)

def _config(key):
    if key in os.environ:
        return os.environ[key]

    my_file = _read_file(os.path.join(base_path, "config.json"))
    if not my_file:
        logger.critical("Main config.json file not found. Exiting.")
        sys.exit()

    try:
        config = json.loads(my_file)
    except Exception as e:
        logger.critical("config.json invalid. Exiting.")
        logger.debug(e)
        sys.exit()

    if config.get(key):
        return config.get(key)
    else:
        logger.critical(f"{key} not found in config.json or in the environment. Exiting.")
        sys.exit()

def _read_file(path):
    file = Path(path)
    if not file.is_file():
        return False

    try:
        file = open(path)
        data = file.read()
        file.close()
    except Exception as e:
        logger.critical("Exception reading file.")
        logger.critical(e)
    return data


def _write_file(path, data):
    try:
        file = open(path, mode="w")
        file.write(data)
        file.close()
    except Exception as e:
        logger.critical("Exception writing file.")
        logger.critical(e)
        return False

    return True
