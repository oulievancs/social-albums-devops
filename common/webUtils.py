"""Utilities regarding WEB and Database Connections"""
from datetime import datetime

from bson import json_util
from flask import json


class WebUtils:

    @staticmethod
    def parse_json(data):
        return json.loads(json_util.dumps(data))

    @staticmethod
    def date_str_to_iso_format(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d")
