"""A script regarding the reading of a csv file that includes User information
and fill a Neo4J database creating associations between users and defining the ids
of artists/bands that they listen.
"""
import json
import logging
import os

import pandas as pd
from dotenv import load_dotenv

from common.neo4JConnection import Neo4JConnection

# Load environment variables from .env file
load_dotenv()

# configure logging level
logging.basicConfig(level=logging.DEBUG)

# Neo4j server information
uri = os.environ.get("DB_NEO4J")
username = os.environ.get("DB_NEO4J_USERNAME")
password = os.environ.get("DB_NEO4J_PASSWORD")
database = os.environ.get("DB_NEO4J_DATABASE_NAME")


class UserNeo4JConnection(Neo4JConnection):
    @staticmethod
    def insert_data(tx, user_data):
        query = (
            "CREATE (u:User {id: $id, first_name: $first_name, last_name: $last_name, "
            "email: $email, gender: $gender, artist_ids: $artist_ids})"
        )
        tx.run(query, **user_data)

        for friend_id in user_data["friends"]:
            tx.run("MATCH (u1:User {id: $id}), (u2:User {id: $friend_id}) "
                   "CREATE (u1)-[:FRIENDS]->(u2)",
                   id=user_data["id"], friend_id=friend_id)


# Connect to Neo4j and execute the script
try:
    with UserNeo4JConnection(uri, username, password, database) as driver:
        with driver.session() as session:
            # Read the modified dataset
            df = pd.read_csv("resources/MOCK_DATA_OUT.csv")

            # Iterate over each row in the DataFrame
            for _, row in df.iterrows():
                # Convert JSON string to list for friends
                friends = json.loads(row["friends"])

                # Prepare data to be inserted into Neo4j
                user_data = {
                    "id": row["id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "gender": row["gender"],
                    "artist_ids": json.loads(row["artist_ids"]),
                    "friends": friends
                }

                # Insert data into Neo4j
                session.write_transaction(UserNeo4JConnection.insert_data, user_data)
    print("User graph created successfully!")
except Exception as e:
    print(f"Error: {e}")
