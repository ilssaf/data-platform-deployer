from abc import ABC
from enum import StrEnum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import yaml
import jsonschema


def _validate_json(json_path: str, schema_path: str) -> bool:
    with open(json_path, "r") as f:
        conf_dict = json.load(f)
    with open(schema_path, "r") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(conf_dict, schema)
    except jsonschema.ValidationError as e:
        print(f"🚨 Validation error: {e.message}")
        return False
    return True

def _validate_yaml(yaml_path: str, schema_path: str = 'schema.json') -> bool:
    with open(yaml_path, "r") as f:
        conf_dict = yaml.safe_load(f)
    with open(schema_path, "r") as f:
        schema = yaml.safe_load(f)
    try:
        jsonschema.validate(conf_dict, schema)
    except jsonschema.ValidationError as e:
        print(f"🚨 Validation error: {e.message}")
        return False
    return True

def validate(file_path: str, schema_path: str) -> bool:
    if file_path.endswith(".json"):
        return _validate_json(file_path, schema_path)
    elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
        return _validate_yaml(file_path, schema_path)
    else:
        raise ValueError("Unknown file format. Must be either JSON or YAML.")


def from_yaml_to_json(yaml_path: str) -> str:
    with open(yaml_path, "r") as f:
        conf_dict = yaml.safe_load(f)
    return json.dump(conf_dict)


def _load_config_from_yaml(yaml_path: str) -> "Config":
    with open(yaml_path, "r") as f:
        conf_dict = yaml.safe_load(f)
    return _load_config(conf_dict)


def _load_config_from_json(json_path: str) -> "Config":
    with open(json_path, "r") as f:
        conf_dict = json.load(f)
    return _load_config(conf_dict)


def load_config_from_file(file_path: str) -> "Config":
    if file_path.endswith(".json"):
        return _load_config_from_json(file_path)
    elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
        return _load_config_from_yaml(file_path)


def _load_config(conf_dict: Dict[str, Any]):
    project = Project(**conf_dict["project"])

    sources = []
    for source in conf_dict["sources"]:
        source_type = source["type"]
        if source_type == "postgres":
            sources.append(Postgres(**source))
        elif source_type == "s3":
            sources.append(S3(**source))
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    kafka_connect = KafkaConnect(**conf_dict["streaming"]["connect"])

    storage = StorageConfig(clickhouse=ClickHouse(**conf_dict["storage"]["clickhouse"]))

    bi = BI(superset=Superset(**conf_dict["bi"]["superset"]))

    return Config(
        project=project,
        sources=sources,
        streaming=Streaming(
            kafka=Kafka(**conf_dict["streaming"]["kafka"]), connect=kafka_connect
        ),
        storage=storage,
        bi=bi,
    )


@dataclass
class Project:
    name: str
    version: str
    description: str


@dataclass
class Source(ABC):
    pass


@dataclass
class RDBMS(ABC):
    host: str
    port: int
    username: str
    password: str
    database: str
    tables: List["Table"]


@dataclass
class Table(ABC):
    name: str
    shema: str


@dataclass
class Postgres(Source, RDBMS):
    name: str
    type: str
    port: int
    username: str
    password: str
    database: str
    tables: List[Table]


@dataclass
class S3(Source):
    name: str
    type: str
    access_key: str
    secret_key: str
    region: str
    bucket: str
    port: str
    data_dir: Optional[str] = None


@dataclass
class Kafka:
    num_brokers: int


@dataclass
class KafkaConnector(ABC):
    pass


@dataclass
class DebeziumSourceConnector(KafkaConnector):
    name: str
    type: str
    config: Dict[str, str]


@dataclass
class DebeziumPostgresSourceConnector(DebeziumSourceConnector):
    database_hostname: str
    database_port: int
    database_user: str
    database_password: str
    database_dbname: str
    database_server_name: str


@dataclass
class KafkaConnect:
    url: str
    connectors: List[KafkaConnector]


@dataclass
class Streaming:
    kafka: Kafka
    connect: KafkaConnect


class ClickHouseTableEngineType(StrEnum):
    KAFKA = "Kafka"
    S3 = "S3"


class ClickHouseTableFormat(StrEnum):
    JSON = "JSON"
    JSONEachRow = "JSONEachRow"


@dataclass
class ClickHouseTableEngine:
    type: ClickHouseTableEngineType
    config: Dict[str, str]


@dataclass
class ClickHouseTable(Table):
    engine: ClickHouseTableEngine
    format: ClickHouseTableFormat


@dataclass
class ClickHouse(RDBMS):
    tables: List[ClickHouseTable]


@dataclass
class StorageConfig:
    clickhouse: ClickHouse


@dataclass
class Superset:
    url: str
    username: str
    password: str
    port: str


@dataclass
class BI:
    superset: Superset


@dataclass
class Config:
    project: Project
    sources: List[Source]
    streaming: Streaming
    storage: StorageConfig
    bi: BI
