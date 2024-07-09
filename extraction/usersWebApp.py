"""An application regarding the Web REST-API that fetched the users from a Neo4J DB
and sends them into a Kafka topic channel"""
import json
import logging
import os
import sys

from fastapi import FastAPI, Security, Path
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from kafka import KafkaProducer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Json

from common.neo4JConnection import Neo4JConnection
from common.webUtils import WebUtils
from deps.auth import get_auth

# Load environment variables from .env file
load_dotenv()

"""Properties regarding the web server configuration."""
TOPIC = os.environ.get("KAFKA_TOPIC_USERS")

"""Properties regarding the Neo4j connection configuration."""
uri = os.environ.get("DB_NEO4J")
username = os.environ.get("DB_NEO4J_USERNAME")
password = os.environ.get("DB_NEO4J_PASSWORD")
database = os.environ.get("DB_NEO4J_DATABASE_NAME")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info('API is starting up')

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

producer = KafkaProducer(bootstrap_servers=[os.environ.get("KAFKA_BROKER")],
                         value_serializer=lambda m: json.dumps(m).encode("ASCII"))

@app.on_event("startup")
async def on_startup():
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)


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

# Email validation regex
email_regex = r"[^@]+@[^@]+\.[^@]+"

"""
A route GET regarding the user with email the requesting email, fetch the user
and its friends. Also, a validator initiated in order to accept only strings that
includes the @.
"""


@app.get("/get_users/{user_email}")
async def get_users(user_email: str = Path(..., description="The email of the user", regex=email_regex),
                    identity: Json = Security(get_auth)):
    logger.debug("Searching for user and its friends regarding name [%s] with identity [%s].", user_email, identity)

    data = search_users(user_email)
    users = WebUtils.parse_json(data)

    send_users_metadata(users)

    return JSONResponse(content=json.loads(users))


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
    logger.debug(record_metadata.topic)
    logger.debug(record_metadata.partition)
    logger.debug(record_metadata.offset)


def on_send_error(excp):
    logger.error("Error occurred on kafka topic sent", exc_info=excp)


"""
Send an artist payload into a Kafka topic named uni-uses as defined
in environment variable KAFKA_TOPIC_USERS.
"""


def send_users_metadata(metadata):
    (producer.send(TOPIC, metadata)
     .add_callback(on_send_success)
     .add_errback(on_send_error))
