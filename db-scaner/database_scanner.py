import pymongo
import time
import requests
from typing import Any
import os
class DataBaseScanner:
    def __init__(self, host: str, user_name: str, password: str, port: int, remote_host: str, remote_host_port: int) -> None:
        self.client = pymongo.MongoClient(f'mongodb://{user_name}:{password}@{host}:{port}/')
        self.collection = self.client["EOL"]["test_results"]

        self.remote_host = remote_host
        self.remote_host_port = remote_host_port

    def scan(self) -> None:
        query = {"is_acknowledged": False}
        while (True):
            test_result = self.collection.find_one(query)
            if test_result is None:
                time.sleep(1)
                continue
            test_result.pop("_id")
            self._publish(test_result)
            time.sleep(0.1)

    def _publish(self, test_result: dict[str, Any]) -> None:
        try:
            client_id = test_result["data"]["client_id"]
            print(f"Posting: {test_result}")
            json_response = requests.post(f"http://{self.remote_host}:{self.remote_host_port}/save", json=test_result).json()
            print(json_response)
            data = json_response.get("data")
            if data is not None and data["ack"]:
                self._acknowledge(client_id)
                return
        
            error = json_response.get("error")
            if error is not None and "Duplicate entry" in error:
                self._acknowledge(client_id)
                return
        except Exception as error:
            print(error)
            exit(1)

    def _acknowledge(self, client_id: str) -> None:
        query = {"data.client_id": client_id}
        update = {"$set": {"is_acknowledged": True}}
        self.collection.update_one(query, update)
        print(f"Acknowledged: {client_id}")

