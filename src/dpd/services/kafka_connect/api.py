from pathlib import Path
import sys
from time import sleep
import requests
from requests.exceptions import ConnectionError
import json
from typing import Dict, Any, List

KAFKA_CONNECT_URL = "http://kafka-connect:8083/connectors"


def create_kafka_connector(url: str, config: Dict[str, Any], retries: int = 10) -> dict:
    for _ in range(retries):
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(config),
            )
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            print("Connection erorr, sleep 10 seconds...")
            sleep(10)


def read_configs_from_dir(dir_path: Path) -> List[Dict[str, Any]]:
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"Directory {dir_path} not exists or not directory")

    configs = []
    for config_file in dir_path.glob("*.json"):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                configs.append(config)
        except json.JSONDecodeError as e:
            print(f"Error reading file {config_file}: {e}")
            continue

    return configs


def push_configs(dir_path: Path):
    configs = read_configs_from_dir(dir_path)
    for c in configs:
        create_kafka_connector(KAFKA_CONNECT_URL, c)


def main():
    push_configs(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
