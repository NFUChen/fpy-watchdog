from dataclasses import dataclass
import datetime
from typing import Any
@dataclass
class TestItem:
    test_class: str
    test_name: str
    test_item: str
    value: float
    units: str
    info: str
    result: str
    spec_type: str
    lower_spec: float
    upper_spec: float
    
    
    @property
    def is_fail(self) -> bool:
        return self.result == "FAIL"

    @property
    def is_final_result(self) -> bool:
        return self.test_class == "FinalResult"
    
    def _is_float_convertible(self, value: any) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def to_dict(self) -> dict[str, Any]:
        
        test_item_dict = {}
        for attr, value in self.__dict__.items():
            if self._is_float_convertible(value):
                test_item_dict[attr] = float(value)
                continue
            if value == "":
                test_item_dict[attr] = None
                continue
            test_item_dict[attr] = value
        
        return test_item_dict

class TestResultParser:
    HEADER_START = "HEADER_START"
    HEADER_END = "HEADER_END"
    BODY_START = "BODY_START"
    BODY_END = "BODY_END"
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        
    def convert_to_snake_case(self, non_snake_case_string: str) -> str:
        words = non_snake_case_string.split()  # Split the input string into individual words
        snake_case_string = "_".join(words).lower()  # Convert words to lowercase and join with underscores
        return snake_case_string
    def _convert_datetime(self, datetime_str: str) -> datetime.datetime:
        datetime_format = "%d/%m/%Y %H:%M:%S"

        return datetime.strptime(datetime_str, datetime_format)
    
    def parse(self) -> dict[str, Any]:
        result = {"header": {}, "failed_items": []}
        is_hedaer_start = False
        is_body_start = False
        with open(self.file_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.replace('"', "").strip()
                if line == self.HEADER_START:
                    is_hedaer_start = True
                    continue
                if line == self.BODY_START:
                    is_body_start = True
                    continue
                if line == self.HEADER_END:
                    is_hedaer_start = False
                    continue
                if line == self.BODY_END:
                    is_body_start = False
                    continue

                if is_hedaer_start:
                    attr, value = [word.strip() for word in line.split(",")]
                    key = self.convert_to_snake_case(attr)
                    result["header"][key] = value
                if is_body_start:
                    test_item = [word.strip() for word in line.split(",")] # ['1505315502,InfoTask,Test Info,Timestamp,1682394493.0,,,COMPLETE,,,\n']
                    test_item = TestItem(*test_item[1:]) # first value is serial, ignore it.
                    test_item_dict = test_item.to_dict()
                    if test_item.is_fail and not test_item.is_final_result:
                        result["failed_items"].append(test_item_dict)
            result["is_pass"] = True if len(result["failed_items"]) == 0 else False
            datetime = f'{result["header"]["test_date"]} {result["header"]["test_start_time"]}'
            result["header"]["test_datetime"] = datetime
            result["header"].pop("test_date")
            result["header"].pop("test_start_time")
            
        return result
        