from enum import Enum


class ServiceType(Enum):
    CLICKHOUSE = "clickhouse"
    KAFKA = "kafka"
    MINIO = "minio"
    POSTGRESQL = "postgresql"
    SUPERSET = "superset"
    KAFKA_UI = "kafka-ui"
    KAFKA_CONNECT = "kafka-connect"
