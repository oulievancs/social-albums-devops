"""An application regarding the Web REST-API that fetched the users from a Neo4J DB
and sends them into a Kafka topic channel"""
import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_parameter_validation import ValidateParameters, Route
from kafka import KafkaProducer

from common.neo4JConnection import Neo4JConnection
from common.webUtils import WebUtils

# Load environment variables from .env file
load_dotenv()

"""Properties regarding the web server configuration."""
TOPIC = os.environ.get("KAFKA_TOPIC_USERS")

"""Properties regarding the Neo4j connection configuration."""
uri = os.environ.get("DB_NEO4J")
username = os.environ.get("DB_NEO4J_USERNAME")
password = os.environ.get("DB_NEO4J_PASSWORD")
database = os.environ.get("DB_NEO4J_DATABASE_NAME")

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers=[os.environ.get("KAFKA_BROKER")],
                         value_serializer=lambda m: json.dumps(m).encode("ASCII")
                         )

"""
A claas regarding a Neo4JConnection implementation declaring also
a select query that can be used to query the Neo4j on Users providing filters.
"""


class UserNeo4JConnection(Neo4JConnection):
    @staticmethod
    def read_users_by_filter(tx, filters):
        # Cypher query to find the user and its friends

        query = (
            """MATCH (user:User {email: $email})
            OPTIONAL MATCH (user)-[:FRIENDS]->(friends:User)
            RETURN user, COLLECT(friends) AS friends"""
        )

        result = tx.run(query, **filters)
        return list(result)  # return a list of Record objects


neo4JConnection = UserNeo4JConnection(uri, username, password, database).driver

"""
A route GET regarding the user with email the requesting email, fetch the user
and its friends. Also, a validator initiated in order to accept only strings that
includes the @.
"""


@app.route("/get_users/<string:user_email>", methods=["GET"])
@ValidateParameters()
def get_user(user_email: str = Route(str, func=WebUtils.generate_date_validation(r"[^@]+@[^@]+\.[^@]+"))):
    app.logger.debug("Searching for user and its friends regarding name [%s].", user_email)

    users = WebUtils.parse_json(search_users(user_email))

    send_users_metadata(users)

    return jsonify(users)


"""Functionality regarding the the indexing of a user by the mail
and its friends."""


def search_users(email):
    with neo4JConnection.session() as session:
        return session.execute_read(
            UserNeo4JConnection.read_users_by_filter,
            {"email": email}
        )


# Log on successful sent.
def on_send_success(record_metadata):
    app.logger.debug(record_metadata.topic)
    app.logger.debug(record_metadata.partition)
    app.logger.debug(record_metadata.offset)


def on_send_error(excp):
    app.logger.error("Error occurred on kafka topic sent", exc_info=excp)


"""
Send an artist payload into a Kafka topic named uni-uses as defined
in environment variable KAFKA_TOPIC_USERS.
"""


def send_users_metadata(metadata):
    (producer.send(TOPIC, metadata)
     .add_callback(on_send_success)
     .add_errback(on_send_error))


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    app.run(host="0.0.0.0", port=5000, debug=True)
