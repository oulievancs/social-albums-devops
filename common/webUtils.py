"""Utilities regarding WEB and Database Connections"""
import logging
import re
import traceback
import uuid
from datetime import datetime, date

from bson import json_util
from flask import json, jsonify


class WebUtils:
    not_found = 404
    internal_error = 500

    @staticmethod
    def parse_json(data):
        return json.loads(json_util.dumps(data))

    @staticmethod
    def date_str_to_iso_format(date_str, format="%Y-%m-%d") -> datetime:
        return datetime.strptime(date_str, format)

    @staticmethod
    def date_to_str(datetime: date | datetime, format="%Y-%m-%d") -> str:
        return datetime.strftime(format)

    @staticmethod
    def dictionary_contains_key(dictionary, key):
        for kkey in dictionary:
            if kkey == key:
                return dictionary[kkey]

        return None

    @staticmethod
    def extract_year(date_str: str) -> int:
        if date_str:
            parts = date_str.split("-")
        else:
            parts = [0]

        return int(parts[0])

    @staticmethod
    def get_a_random_string() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_regex_pattern(strings) -> re.Pattern[str]:
        # Escape special characters in each string and join them with '|'
        escaped_strings = map(re.escape, strings)
        pattern = '|'.join(escaped_strings)

        # Create a regex pattern that matches any of the strings
        regex_pattern = re.compile(f"""^({pattern})""")

        return regex_pattern

    """Generates a signleton set of strings between the given number. (e.g. 2015, 2019 -> (2015, 2016, 2017, 2018, 2019)."""

    @staticmethod
    def generate_numbers_as_strings(nfrom: int, nto: int) -> [str]:
        res = set()

        for i in range(nfrom, nto + 1):
            res.add(str(i))

        return res

    """Generates and returns the validation lambda regarding the given pattern."""

    @staticmethod
    def generate_date_validation(pattern) -> lambda m: bool:
        return lambda m: WebUtils._date_validation(pattern, m)

    """Applies the pattern as a regular expression on given value."""

    @staticmethod
    def _date_validation(pattern, value: str) -> bool:
        res = True if re.fullmatch(pattern, value) else False

        return res

    """Return the begin of year in given format regarding the given year."""

    @staticmethod
    def start_of_year(year: int, format="%Y-%m-%d") -> str:
        return datetime(year, 1, 1).strftime(format)

    """Return the end of year in given format regarding the given year."""

    @staticmethod
    def end_of_year(year: int, format="%Y-%m-%d") -> str:
        return datetime(year, 12, 31).strftime(format)

    @staticmethod
    def handle_error(error):
        logging.error(f"""Http Error: {error}!""")

        code = WebUtils.internal_error
        msg = "Unknown error occurred!"

        if hasattr(error, "code") and error.code == WebUtils.internal_error:
            msg += f"""An internal server error occurred!"""
        else:
            code = error.code if hasattr(error, "code") else WebUtils.internal_error

            msg = error.description if hasattr(error, "description") else \
                (error.message if hasattr(error, "message") else None)

        logging.error(traceback.format_exc())

        return jsonify(error=str(msg)), code

    """Map a tuple into a dictionary containing the given properties' values."""

    @staticmethod
    def map_tuple(tuple, properties: [str]):
        res = {}
        for index, t in enumerate(tuple):
            if len(properties) > index:
                res[properties[index]] = t

        return res

    """Generates the %s parameters on given count regarding queries."""

    @staticmethod
    def generate_parameters(count: int) -> str:
        params = []
        for i in range(count):
            params.append("%s")

        return ", ".join(params)

    """Converts from ISO string format and remove the time. Check also that is in IS) 8601 format."""

    @staticmethod
    def date_no_time_from_iso_string(date_string: str) -> date | None:
        if date_string is None or not WebUtils._is_iso8601_format(str(date_string)):
            return None
        return datetime.fromisoformat(str(date_string)).date()

    @staticmethod
    def _is_iso8601_format(s):
        try:
            # Attempt to parse the string as a datetime with ISO 8601 format
            datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False
