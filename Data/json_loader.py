import json
import os

def load_json(file_name: str):
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'r') as file:
        return json.load(file)