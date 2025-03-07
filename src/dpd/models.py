from abc import ABC
from enum import StrEnum
from typing import List, Dict, Optional
from dataclasses import dataclass
import json


def load_config_from_json(json_path: str) -> "Config":
    with open(json_path, "r") as f:
        conf_dict = json.load(f)

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
