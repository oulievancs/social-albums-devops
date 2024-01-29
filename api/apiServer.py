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

"""Route accepting a user's mail that belongs to a user and return a suggestion of albums and artists
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


"""Route accepting a user's mail that belongs to a user and returns a suggestion of artists to listen."""


@app.route("/suggest_common/<string:email>", methods=["GET"])
@ValidateParameters()
def suggest_artists(email: str = Route(str, func=WebUtils.generate_date_validation(r"[^@]+@[^@]+\.[^@]+"))):
    result = {}

    connection = None
    try:
        connection = mysqlCon.pool_connection()
        result = get_artists_that_friends_listen_on_common_descriptors(email, connection)
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
        raise abort(WebUtils.NOT_FOUND, description=f"""User requested with email [{email}] not found!""")


"""Get the albums regarding the provided artist."""


def get_artist_albums(artist_id: int, connection: MySQLResult) -> [{"id": int, "name": str, "release_date": str}]:
    res_albums = mysqlCon.execute(
        f"""SELECT a.id, a.name, a.release_date FROM album AS a WHERE a.artist_id = %s""",
        args=(artist_id,),
        mysqlResult=connection
    )

    if res_albums.rowcount > 0:
        albums = list(WebUtils.map_tuple(t, ["id", "name", "release_date"]) for t in res_albums.fetchall)

        for album in albums:
            album["release_date"] = WebUtils.date_to_str(album["release_date"])

        return albums
    else:
        return list()


"""Retrieve all the artists that friends of user listen to."""


def get_friends_of_user(user_id: int, connection: MySQLResult) -> set[int]:
    res_friends = mysqlCon.execute(
        f"""SELECT a.friend_user_id FROM friendship AS a WHERE a.user_id = %s""",
        args=(user_id,),
        mysqlResult=connection
    )

    if res_friends.rowcount > 0:
        return {friend_id[0] for friend_id in res_friends.fetchall}
    else:
        return set()


def get_artists_that_users_friends_listen(friend_user_ids: [int], connection: MySQLResult) -> set[int]:
    return get_artists_in_users(friend_user_ids, None, connection)


def get_artists_regarding_user(user_id: int, connection: MySQLResult) -> set[int]:
    return get_artists_in_users([user_id], None, connection)


"""Functionality regarding the user's artists listened excluding dummy artists."""


def get_artists_in_users(user_ids: [int], filters: {"descriptors": set[int]}, connection: MySQLResult) -> set[int]:
    if filters is None or filters["descriptors"]:
        logging.log(logging.INFO, f"ffffffffffffffffff {tuple(user_ids) + (WebUtils.DUMMY_ARTIST_REGEX,)}")

        res_artists = mysqlCon.execute(
            f"""SELECT DISTINCT a.artist_id FROM listen AS a
            LEFT JOIN artist AS b ON a.artist_id = b.id
            WHERE a.user_id IN ({WebUtils.generate_parameters(len(user_ids))}) AND NOT b.name REGEXP %s""",
            args=(tuple(user_ids) + (WebUtils.DUMMY_ARTIST_REGEX,)),
            mysqlResult=connection
        )
    else:
        res_artists = mysqlCon.execute(
            f"""SELECT DISTINCT a.artist_id FROM listen AS a
            LEFT JOIN artist AS d ON a.artist_id = d.id
            LEFT JOIN descriptors_asoc AS b ON a.artist_id = b.artist_id
            LEFT JOIN descriptors AS c ON b.descriptor_id = c.id
            WHERE a.user_id IN ({WebUtils.generate_parameters(len(user_ids))})
            AND c.id IN ({WebUtils.generate_parameters(len(filters['descriptors']))})
            AND NOT b.name REGEXP %s""",
            args=(tuple(user_ids) + tuple(filters['descriptors']) + (WebUtils.DUMMY_ARTIST_REGEX,))
        )

    if res_artists.rowcount > 0:
        return {artist_id[0] for artist_id in res_artists.fetchall}
    else:
        return set()


"""Retrieve the artist's information with id's provied."""


def get_artists(artist_ids: [int], connection: MySQLResult) -> {"id": int, "year": str, "name": str,
                                                                "albums": [
                                                                    {"id": int, "name": str, "release_date": str}]
                                                                }:
    res_artists = mysqlCon.execute(
        f"""SELECT a.id, a.year, a.name FROM artist AS a WHERE a.id IN({WebUtils.generate_parameters(len(artist_ids))})""",
        args=(tuple(artist_ids)),
        mysqlResult=connection
    )

    if res_artists.rowcount > 0:
        res = list(WebUtils.map_tuple(artis, ["id", "year", "name"]) for artis in res_artists.fetchall)

        for artist in res:
            artist["albums"] = get_artist_albums(artist["id"], connection)

        return res
    else:
        return list()


def get_descriptors_regarding_user(user_id: int, connection: MySQLResult) -> set[str]:
    res_listen = mysqlCon.execute(
        f"""SELECT DISTINCT c.id FROM listen AS a
        LEFT JOIN descriptors_asoc AS b ON a.artist_id = b.artist_id AND b.descriptor_type = %s
        LEFT JOIN descriptors AS c ON b.descriptor_id = c.id
        WHERE a.user_id = %s""",
        args=("DESCRIPTOR", user_id),
        mysqlResult=connection
    )

    if res_listen.rowcount > 0:
        return {tpl[0] for tpl in res_listen.fetchall}
    else:
        return set()


"""Suggestions of artists regarding the artists that the user's email not has in
its favorite list but its friends like it."""


def get_artists_that_friends_listen(user_email: str, connection: MySQLResult):
    user = get_user_by_email(user_email, connection)
    friends_ids = get_friends_of_user(user["id"], connection)
    artists_of_friends = get_artists_that_users_friends_listen(friends_ids, connection)

    user_artists = get_artists_in_users([user["id"]], None, connection)

    excluded_user_s_artists = set(f for f in artists_of_friends if f not in user_artists)

    return get_artists(excluded_user_s_artists, connection)


def get_artists_that_friends_listen_on_common_descriptors(user_email: str, connection: MySQLResult):
    user = get_user_by_email(user_email, connection)
    friends_ids = get_friends_of_user(user["id"], connection)
    descriptors = get_descriptors_regarding_user(user["id"], connection)

    user_artists = get_artists_in_users([user["id"]], None, connection)

    artists_of_friends = get_artists_in_users(friends_ids, {"descriptors": descriptors}, connection)

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
