"""An application regarding a Web REST-API that fetches the artists from a MongoDB
and sends them into a Kafka topic channel."""
import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_parameter_validation import ValidateParameters
from flask_parameter_validation.parameter_types.route import Route
from kafka import KafkaProducer

from common.mongoDb import MyMongoClient
from common.webUtils import WebUtils

# Load environment variables from .env file
load_dotenv()

# MongoDB's connection settings
mongo_uri = os.environ.get("MONGODB_URI")
database_name = os.environ.get("MONGODB_NAME")
collection_name = os.environ.get("MONGODB_COLLECTION_NAME")

TOPIC = os.environ.get("KAFKA_TOPIC_ARTISTS")

# Connect to MongoDB
collection, client = MyMongoClient.connect_to_mongodb(mongo_uri, database_name, collection_name)

app = Flask(__name__)

"""
A route GET regarding the artists that are located on a MondoDB collection,
that fetched the artists who released from the given year_from year until
the given year_to year.
"""


@app.route("/get_artists/<string:year_from>/<string:year_to>", methods=["GET"])
@ValidateParameters()
def get_artists(year_from: str = Route(str, func=WebUtils.generate_date_validation(r"^\d{4}$")),
                year_to: str = Route(str, func=WebUtils.generate_date_validation(r"^\d{4}$"))):
    vyear_from = WebUtils.start_of_year(int(year_from))
    vyear_to = WebUtils.end_of_year(int(year_to))

    app.logger.debug(f"""Searching for Artists the released date between {vyear_from} and {vyear_to}.""")

    artists = WebUtils.parse_json(collection.find({"year": {"$gte": vyear_from, "$lte": vyear_to}}))

    send_artists_metadata(artists)
    return jsonify(artists)


producer = KafkaProducer(bootstrap_servers=[os.environ.get("KAFKA_BROKER")],
                         value_serializer=lambda m: json.dumps(m).encode("ASCII")
                         )


# Log on successful sent.
def on_send_success(record_metadata):
    app.logger.debug(record_metadata.topic)
    app.logger.debug(record_metadata.partition)
    app.logger.debug(record_metadata.offset)


def on_send_error(excp):
    app.logger.error("Error occurred on kafka topic sent", exc_info=excp)


"""
Send an artist payload into a Kafka topic named uni-artist as defined
in environment variable KAFKA_TOPIC_ARTISTS.
"""


def send_artists_metadata(metadata):
    (producer.send(TOPIC, metadata)
     .add_callback(on_send_success)
     .add_errback(on_send_error))


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    app.run(host="0.0.0.0", port=5000, debug=True)
