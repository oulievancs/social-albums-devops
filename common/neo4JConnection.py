"""A unit regarding a Neo4J Functionalities declaring an Abstract class of Neo4JConnection."""
from abc import ABC

from neo4j import GraphDatabase, Session


class Neo4JConnection(ABC):
    def __init__(self, uri, user, password, database):
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def session(self) -> Session:
        return self.driver.session(database=self.database)

    def __enter__(self):
        # Open the file when entering the "with" block
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the file when exiting the "with" block
        if self.driver:
            self.close()
