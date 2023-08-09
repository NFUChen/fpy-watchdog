from typing import Callable
import socket
import os
from test_result_parser import TestResultParser
from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler
from logger import Logger
from database_manager import db_manager

class InvalidLoggerError(Exception):
    pass

logger = Logger("error.log")

def publish_and_log_error(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        try:
            return func(*args, **kwargs)
        except Exception as error:
            global logger
            logger.error(error)
    return wrapper

class EventHandler(FileSystemEventHandler):
    def __init__(self, valid_extensions: list[str]) -> None:
        self.self_host_name = socket.gethostname()
        self.logger = logger
        self.valid_extensions = valid_extensions
    
    
    @publish_and_log_error
    def on_created(self, event: FileSystemEvent) -> None:

        current_file_name = os.path.basename(event.src_path)
        if not self.__is_valid_file_extension(current_file_name):
            return
        parser = TestResultParser(event.src_path)

        parsed_result_dict = parser.parse()
        db_manager.insert_one("EOL", "test_results", parsed_result_dict)
        print(parsed_result_dict)
            
    def on_moved(self, event: FileSystemEvent) -> None:
        pass

    def on_deleted(self, event: FileSystemEvent) -> None:
        pass

    def __is_valid_file_extension(self, file_name:str) -> bool:
        file_name_extension = file_name.split(".").pop()
        for extension in self.valid_extensions:
            if extension == file_name_extension:
                return True
        return False
