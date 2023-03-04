from __future__ import annotations
from dotenv import load_dotenv
import os
import pymongo
from pymongo.database import Database as MongoDatabase

load_dotenv()


class MongoDatabase:
    def __init__(self) -> None:
        self._client: pymongo.MongoClient = None
        self._database: MongoDatabase = None

    @property
    def client(self) -> pymongo.MongoClient:
        if self._client is None:
            raise Exception("Client not connected")

        return self._client

    @property
    def connected_database(self) -> MongoDatabase:
        if self._database is None:
            raise Exception("Database not connected")

        return self._database

    def connect_database(self, database_name: str) -> None:
        self._client = pymongo.MongoClient(
            f"mongodb+srv://{os.getenv('MONGO_DB_USER')}:{os.getenv('MONGO_DB_PASSWORD')}@novo.4b3bqfk.mongodb.net/?retryWrites=true&w=majority"
        )
        self._database = self._client.get_database(database_name)

    def close_connection(self) -> None:
        if isinstance(self._client, pymongo.MongoClient):
            self._client.close()

    def connect_to_F1_Calendar(self) -> tuple[MongoDatabase, pymongo.MongoClient]:
        self.connect_database("F1_Calendar")
        return self, self.connected_database
