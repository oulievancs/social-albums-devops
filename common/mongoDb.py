"""Regarding functionalities of MongoDB."""
from pymongo import MongoClient
from pymongo.collection import Collection


class MyMongoClient:
    @staticmethod
    def connect_to_mongodb(mongo_uri, database_name, collection_name) -> tuple[Collection, MongoClient]:
        try:
            client = MongoClient(mongo_uri)
            db = client[database_name]
            collection = db[collection_name]
            return collection, client
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    @staticmethod
    def close_mongodb_connection(client):
        try:
            client.close()
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")
            raise
