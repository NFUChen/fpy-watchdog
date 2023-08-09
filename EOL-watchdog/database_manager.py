from typing import Any
import pymongo
import uuid
class DataBaseManager:
    def __init__(self, host: str, user_name: str, password: str, port: int) -> None:
        self.client = pymongo.MongoClient(f'mongodb://{user_name}:{password}@{host}:{port}/')

    def _create_uuid_document(self, document: dict[str, Any]) -> dict:
        return {
            "data": {**document, "client_id": str(uuid.uuid4())},
            "is_acknowledged": False
        }
    
    def insert_one(self, db_name: str, collection_name: str, document: dict) -> None:
        db = self.client[db_name]
        collection = db[collection_name]
        uuid_doc = self._create_uuid_document(document)
        collection.insert_one(uuid_doc)

db_manager = DataBaseManager("fpy-watchdog-db", "root", "sramsram-admin", 27017)