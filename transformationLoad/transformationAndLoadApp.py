"""A unit regarding consuming data by uni-artists and uni-users, transformed
into associations between artists and users and write out into a MySql database."""
import json
import logging
import os
import traceback
from threading import Thread

from dotenv import load_dotenv
from kafka import KafkaConsumer

from common.mySQLDb import MySqlConnection
from common.webUtils import WebUtils

# Load environment variables from .env file
load_dotenv()

MYSQL_DB_HOST = os.environ.get("MYSQL_DB_HOST")
MYSQL_DB_PORT = os.environ.get("MYSQL_DB_PORT")
MYSQL_DB_NAME = os.environ.get("MYSQL_DB_NAME")
MYSQL_DB_USERNAME = os.environ.get("MYSQL_DB_USERNAME")
MYSQL_DB_PASSWORD = os.environ.get("MYSQL_DB_PASSWORD")

KAFKA_BROKER = os.environ.get("KAFKA_BROKER")

TOPIC_USERS = os.environ.get("KAFKA_TOPIC_USERS")
TOPIC_ARTISTS = os.environ.get("KAFKA_TOPIC_ARTISTS")

mysqlCon = MySqlConnection(MYSQL_DB_HOST, MYSQL_DB_NAME, MYSQL_DB_USERNAME, MYSQL_DB_PASSWORD, MYSQL_DB_PORT)

"""Functionality regarding the consuming of user, and write it into the MySQL DB."""


def consume_user(users, connection):
    logging.log(logging.INFO, f"Consuming user. {users}")

    for user in users:
        vuser = user["user"]

        vuserId = add_user(vuser, connection)

        friendIds = []
        for friend in user["friends"]:
            add_user_id = add_user(friend, connection)

            if add_user_id is not None:
                friendIds.append(add_user_id)

        for friendId in friendIds:
            resFriendship = mysqlCon.execute(
                f"""SELECT a.id, a.user_id, a.friend_user_id FROM friendship AS a WHERE a.user_id = %s AND a.friend_user_id = %s""",
                args=(vuserId, friendId),
                mysqlResult=connection
            )

            if resFriendship.rowcount < 1:
                resFriendship = mysqlCon.execute(
                    f"""INSERT INTO friendship (user_id, friend_user_id) VALUES (%s, %s)""",
                    args=(vuserId, friendId),
                    mysqlResult=connection
                )

                connection.commit()

                resFriendUserId = resFriendship.lastrowid
            else:
                resFriendUserId = resFriendship.fetchone[0]


"""Functionality regarding the user creation. Also, be used in order to persist a user's friends."""


def add_user(user, connection):
    if user is None:
        return None

    res = mysqlCon.execute(
        f"""SELECT a.id, a.first_name, a.last_name, a.email, a.gender FROM user AS a WHERE a.email = %s""",
        args=(user["email"],),
        mysqlResult=connection
    )

    if res.rowcount < 1:
        res = mysqlCon.execute(
            f"""INSERT INTO user (first_name, last_name, email, gender, ref_aa) VALUES (%s, %s, %s, %s, %s)""",
            args=(user["first_name"], user["last_name"], user["email"], user["gender"], user["id"]),
            mysqlResult=connection

        )

        user_actual_id = res.lastrowid
    else:
        user_actual_id = res.fetchone[0]

    if user["artist_ids"] is not None:
        for listen_ref_id in user["artist_ids"]:
            resListns = mysqlCon.execute(
                f"""SELECT a.id, a.user_id, a.artist_id FROM listen AS a 
                 LEFT JOIN artist AS b ON a.artist_id = b.id WHERE a.user_id = %s AND b.ref_aa = %s""",
                args=(user_actual_id, listen_ref_id),
                mysqlResult=connection
            )

            if resListns.rowcount < 1:
                artist_actual_id = create_dummy_artist_if_not_exists(listen_ref_id, connection)

                resListns = mysqlCon.execute(
                    f"""INSERT INTO listen (user_id, artist_id) VALUES (%s, %s)""",
                    args=(user_actual_id, artist_actual_id),
                    mysqlResult=connection
                )

    connection.commit()

    return user_actual_id


"""Functionality that searched for an artist using the ref_aa column. In the case
artist was not found then a dummy row created with a dummy name. The actual artist id is returned.
"""


def create_dummy_artist_if_not_exists(ref_aa, connection):
    resArtistRef = mysqlCon.execute(
        f"""SELECT a.id, a.year, a.name, a.ref_aa FROM artist AS a WHERE a.ref_aa = %s""",
        args=(ref_aa,),
        mysqlResult=connection
    )

    if resArtistRef.rowcount < 1:
        resArtistRef = mysqlCon.execute(
            f"""INSERT INTO artist (name, ref_aa) VALUES (%s, %s)""",
            args=(f"""DUMMY ARTIST {WebUtils.get_a_random_string()}""", ref_aa),
            mysqlResult=connection
        )

        connection.commit()

        artist_actual_id = resArtistRef.lastrowid
    else:
        artist_actual_id = resArtistRef.fetchone[0]

    return artist_actual_id


"""Functionality regarding the consuming of artist, and write it into the MySQL DB."""


def consume_artist(artists, connection):
    logging.log(logging.INFO, f"Consuming artist. {artists}")

    for artist in artists:
        res = mysqlCon.execute(
            f"""SELECT a.id, a.name, a.year, a.ref_aa FROM artist AS a WHERE a.ref_aa = %s""",
            args=(artist["aa"],),
            mysqlResult=connection)

        if res.rowcount < 1:
            res = mysqlCon.execute(f"""INSERT INTO artist (name, year, ref_aa) VALUES 
            (%s, %s, %s)""",
                                   args=(artist["artist_name"],
                                         WebUtils.extract_year(WebUtils.dictionary_contains_key(artist, "year")),
                                         artist["aa"]),
                                   mysqlResult=connection)

            artId = res.lastrowid
        else:
            if not res.fetchone[1] == artist["artist_name"]:
                res_update = mysqlCon.execute(
                    f"""UPDATE artist AS a SET a.name = %s, a.year = %s WHERE a.ref_aa = %s""",
                    (artist["artist_name"], WebUtils.dictionary_contains_key(artist, "year")),
                    mysqlResult=connection
                )

                connection.commit()

            artId = res.fetchone[0]

        for album in artist["albums"]:
            resAl = mysqlCon.execute(f"""SELECT a.id, a.name, a.reviews, a.avg_rating, a.ratings, a.artist_id
            FROM album AS a WHERE a.name = %s AND a.artist_id = %s""",
                                     args=(album["release_name"], artId),
                                     mysqlResult=connection)

            if resAl.rowcount < 1:
                resAl = mysqlCon.execute(f"""INSERT INTO album (name, reviews, avg_rating, ratings, artist_id) VALUES
                (%s, %s, %s, %s, %s)""",
                                         args=(album["release_name"], album["review_count"], album["avg_rating"],
                                               album["rating_count"], artId),
                                         mysqlResult=connection)

                albumId = resAl.lastrowid
            else:
                albumId = res.fetchone[0]

            persist_artist_descriptors(artist["descriptors"], artId, "descriptors", "DESCRIPTOR", connection)
            persist_artist_descriptors(artist["primary_genres"], artId, "primary_genres", "PRIMARY_GENRE", connection)
            persist_artist_descriptors(artist["secondary_genres"], artId, "secondary_genres", "SECONDARY_GENRE",
                                       connection)


"""Functionality regarding update and fill artist's descriptors."""


def persist_artist_descriptors(descriptors, artist_id, table_name, descr_type, connection):
    try:
        for descr in set(descriptors):
            resDe = mysqlCon.execute(
                f"""SELECT a.id, a.description FROM {table_name} AS a WHERE a.description = %s""",
                args=(descr,),
                mysqlResult=connection)

            if resDe.rowcount < 1:
                resDe = mysqlCon.execute(f"""INSERT INTO {table_name} (description) VALUES(%s)""",
                                         args=(descr,),
                                         mysqlResult=connection)

                descriptorId = resDe.lastrowid
            else:
                descriptorId = resDe.fetchone[0]

            resDeAsoc = mysqlCon.execute(f"""SELECT a.id, a.artist_id, a.descriptor_id, a.descriptor_type FROM descriptors_asoc AS a
            WHERE a.artist_id = %s AND a.descriptor_id = %s""",
                                         args=(artist_id, descriptorId),
                                         mysqlResult=connection)

            if resDeAsoc.rowcount < 1:
                resDeAsoc = mysqlCon.execute(f"""INSERT INTO descriptors_asoc (artist_id, descriptor_id, descriptor_type) VALUES
            (%s, %s, %s)""", args=(artist_id, descriptorId, descr_type), mysqlResult=connection)

        connection.commit()
    except Exception as e:
        logging.log(logging.ERROR, f"Error while executing {e}, {descriptors}")

        raise e


"""Main functionality regarding the Consumer of Users Topic[uni-users]."""


def main_users():
    consumer_users = KafkaConsumer(TOPIC_USERS, bootstrap_servers=KAFKA_BROKER,
                                   value_deserializer=lambda m: json.loads(m.decode("ASCII")))
    connection = None

    for user in consumer_users:
        try:
            connection = mysqlCon.pool_connection()

            consume_user(user.value, connection)

            connection.commit()
        except Exception as e:
            logging.log(logging.ERROR, f"Error while executing user_consuming. {e}, {traceback.format_exc()}")

            connection.rollback()
        finally:
            try:
                if connection is not None:
                    connection.close_connection()
            except Exception as e_in:
                logging.log(logging.ERROR, f"Error while executing artist_consuming. {e_in}, {traceback.format_exc()}")


"""Main functionality regarding the Consumer of Artists Topic[uni-artists]."""


def main_artists():
    consumer_artists = KafkaConsumer(TOPIC_ARTISTS, bootstrap_servers=KAFKA_BROKER,
                                     value_deserializer=lambda m: json.loads(m.decode("ASCII")))

    for artist in consumer_artists:
        connection = None

        try:
            connection = mysqlCon.pool_connection()

            consume_artist(artist.value, connection)

            connection.commit()
        except Exception as e:
            logging.log(logging.ERROR, f"Error while executing artist_consuming. {e}, {traceback.format_exc()}")

            connection.rollback()

        finally:
            try:
                if connection is not None:
                    connection.close_connection()
            except Exception as e_in:
                logging.log(logging.ERROR, f"Error while executing artist_consuming. {e_in}, {traceback.format_exc()}")


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    thread_users = Thread(target=main_users)
    thread_artists = Thread(target=main_artists)

    thread_users.start()
    thread_artists.start()

    thread_users.join()
    thread_artists.join()
