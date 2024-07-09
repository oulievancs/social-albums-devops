"""An application regarding a Web REST-API that fetches the artists from a MongoDB
and sends them into a Kafka topic channel."""
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

from common.mongoDb import MyMongoClient
from common.webUtils import WebUtils
from deps.auth import get_auth

# Load environment variables from .env file
load_dotenv()

# MongoDB's connection settings
mongo_uri = os.environ.get("MONGODB_URI")
database_name = os.environ.get("MONGODB_NAME")
collection_name = os.environ.get("MONGODB_COLLECTION_NAME")

TOPIC = os.environ.get("KAFKA_TOPIC_ARTISTS")

# Connect to MongoDB
collection, client = MyMongoClient.connect_to_mongodb(mongo_uri, database_name, collection_name)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
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


@app.on_event("startup")
async def on_startup():
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)


"""
A route GET regarding the artists that are located on a MondoDB collection,
that fetched the artists who released from the given year_from year until
the given year_to year.
"""


@app.get("/get_artists/{year_from}/{year_to}")
def get_artists(year_from: str = Path(..., func=WebUtils.generate_date_validation(r"^\d{4}$")),
                year_to: str = Path(..., func=WebUtils.generate_date_validation(r"^\d{4}$")),
                identity: Json = Security(get_auth)):
    vyear_from = WebUtils.start_of_year(int(year_from))
    vyear_to = WebUtils.end_of_year(int(year_to))

    logger.debug(
        f"""Searching for Artists the released date between {vyear_from} and {vyear_to} with identity {identity}.""")

    data = collection.find({"year": {"$gte": vyear_from, "$lte": vyear_to}})
    artists = WebUtils.parse_json(data)

    send_artists_metadata(artists)
    return JSONResponse(content=json.loads(artists))


producer = KafkaProducer(bootstrap_servers=[os.environ.get("KAFKA_BROKER")],
                         value_serializer=lambda m: json.dumps(m).encode("ASCII"))


# Log on successful sent.
def on_send_success(record_metadata):
    logger.debug(record_metadata.topic)
    logger.debug(record_metadata.partition)
    logger.debug(record_metadata.offset)


def on_send_error(excp):
    logger.error("Error occurred on kafka topic sent", exc_info=excp)


"""
Send an artist payload into a Kafka topic named uni-artist as defined
in environment variable KAFKA_TOPIC_ARTISTS.
"""


def send_artists_metadata(metadata):
    (producer.send(TOPIC, metadata)
     .add_callback(on_send_success)
     .add_errback(on_send_error))
