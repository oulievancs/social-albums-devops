"""Unit regarding api server for getting date from the transformed data are located
in a MySQL database and apply intelligent functionalities."""
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, abort
from flask_parameter_validation import Route, ValidateParameters

from common.mySQLDb import MySqlConnection, MySQLResult
from common.webUtils import WebUtils

# Load environment variables from .env file
load_dotenv()

"""Properties regarding the web server configuration."""
PORT = os.environ.get("API_SERVER_PORT")

"""Properties regarding the database."""
MYSQL_DB_HOST = os.environ.get("MYSQL_DB_HOST")
MYSQL_DB_PORT = os.environ.get("MYSQL_DB_PORT")
MYSQL_DB_NAME = os.environ.get("MYSQL_DB_NAME")
MYSQL_DB_USERNAME = os.environ.get("MYSQL_DB_USERNAME")
MYSQL_DB_PASSWORD = os.environ.get("MYSQL_DB_PASSWORD")

mysqlCon = MySqlConnection(MYSQL_DB_HOST, MYSQL_DB_NAME, MYSQL_DB_USERNAME, MYSQL_DB_PASSWORD, MYSQL_DB_PORT)

app = Flask(__name__)

"""Route regarding accept a mail that belongs to a user and return a suggestion of albums and artists
to listen."""


@app.route("/suggest_albums/<string:email>", methods=["GET"])
@ValidateParameters()
def suggest_albums(email: str = Route(str, func=WebUtils.generate_date_validation(r"[^@]+@[^@]+\.[^@]+"))):
    result = {}

    connection = None
    try:
        connection = mysqlCon.pool_connection()
        result = get_artists_that_friends_listen(email, connection)
    finally:
        if connection is not None:
            connection.close_connection()

    return jsonify(result)


"""Retrieves a user by the provided email address."""


def get_user_by_email(email: str, connection: MySQLResult) -> {"id": int, "email": str, "first_name": str,
                                                               "last_name": str,
                                                               "gender": str, "ref_aa": int}:
    res_user = mysqlCon.execute(
        f"""SELECT a.id, a.email, a.first_name, a.last_name, a.gender, a.ref_aa FROM user AS a WHERE a.email = %s""",
        args=(email,),
        mysqlResult=connection
    )

    if res_user.rowcount > 0:
        return WebUtils.map_tuple(res_user.fetchone, ["id", "email", "first_name", "last_name", "gender", "ref_aa"])
    else:
        raise abort(WebUtils.not_found, description=f"""User requested with email [{email}] not found!""")


def get_friends_of_user(user_id: int, connection: MySQLResult):
    uniq_set_of_friends = set()

    res_friends = mysqlCon.execute(
        f"""SELECT a.friend_user_id FROM friendship AS a WHERE a.user_id = %s""",
        args=(user_id,),
        mysqlResult=connection
    )

    if res_friends.rowcount > 0:
        for friend_id in res_friends.fetchall:
            uniq_set_of_friends.add(friend_id[0])

    return uniq_set_of_friends


def get_artists_that_users_friends_listen(friend_user_ids: [int], connection: MySQLResult) -> set[int]:
    return get_artists_in_users(friend_user_ids, connection)


def get_artists_regarding_user(user_id: int, connection: MySQLResult) -> set[int]:
    return get_artists_in_users([user_id], connection)


"""Functionality regarding the user's artists listened."""


def get_artists_in_users(user_ids: [int], connection: MySQLResult) -> set[int]:
    uniq_set_of_artists = set()
    res_artists = mysqlCon.execute(
        f"""SELECT a.artist_id FROM listen AS a WHERE a.user_id IN ({WebUtils.generate_parameters(len(user_ids))})""",
        args=(tuple(user_ids)),
        mysqlResult=connection
    )

    if res_artists.rowcount > 0:
        for artist_id in res_artists.fetchall:
            uniq_set_of_artists.add(artist_id[0])

    return uniq_set_of_artists


"""Retrieve the artist's information with id's provied."""


def get_artists(artist_ids: [int], connection: MySQLResult) -> {"id": int, "year": str, "name": str}:
    artists = []

    res_artists = mysqlCon.execute(
        f"""SELECT a.id, a.year, a.name FROM artist AS a WHERE a.id IN({WebUtils.generate_parameters(len(artist_ids))})""",
        args=(tuple(artist_ids)),
        mysqlResult=connection
    )

    if res_artists.rowcount > 0:
        for artis in res_artists.fetchall:
            artists.append(WebUtils.map_tuple(artis, ["id", "year", "name"]))

    return artists


"""Suggestions of artists regarding the artists that the user's email not has in
its favorite list but its friends like it."""


def get_artists_that_friends_listen(user_emai: str, connection: MySQLResult):
    user = get_user_by_email(user_emai, connection)
    friends_ids = get_friends_of_user(user["id"], connection)
    artists_of_friends = get_artists_that_users_friends_listen(friends_ids, connection)

    user_artists = get_friends_of_user(user["id"], connection)

    excluded_user_s_artists = set(f for f in artists_of_friends if f not in user_artists)

    return get_artists(excluded_user_s_artists, connection)


# Handle HTTP errors with a JSON response
@app.errorhandler(Exception)
def http_error(error):
    return WebUtils.handle_error(error)


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    app.run(host="0.0.0.0", port=PORT, debug=True)
