from pathlib import Path
from dpd.models import Postgres, Kafka, Project, S3, Source
from typing import List
import os
import json
from dpd.enums import ServiceType

from dpd.generation.secret import env_manager
from dpd.services.kafka_connect.plugins import download_and_extract_archive, move_file

"""
  config-loader:
    image: python:3.9-slim
    container_name: kafka-connect-config-loader
    volumes:
      - ./kafka_connect:/configs
      - /Users/hamidullin_ii/repos/data-platform-deployer/src/dpd/services/kafka_connect/api.py:/app.py
    depends_on:
      - kafka-connect
    networks:
    - data-platform-12_network
    command: >
      sh -c "sleep 30 && pip install requests && python app.py /configs"

"""


class KafkaConnectService:
    type = ServiceType.KAFKA_CONNECT

    @staticmethod
    def generate_docker_service(project: Project, kafka: Kafka):
        return {
            "kafka-connect": {
                "container_name": f"{project.name}__kafka_connect".replace("-", "_"),
                "image": "debezium/connect:3.0.0.Final",
                "ports": ["8083:8083"],
                "volumes": ["./kafka_connect/plugins:/kafka/connect/plugins"],
                "environment": {
                    "BOOTSTRAP_SERVERS": ",".join(
                        f"kafka-{i}:9092" for i in range(kafka.num_brokers)
                    ),
                    "GROUP_ID": "kafka-connect-cluster",
                    "CONFIG_STORAGE_TOPIC": "connect-configs",
                    "OFFSET_STORAGE_TOPIC": "connect-offsets",
                    "STATUS_STORAGE_TOPIC": "connect-status",
                    "CONFIG_STORAGE_REPLICATION_FACTOR": "1",
                    "OFFSET_STORAGE_REPLICATION_FACTOR": "1",
                    "KEY_CONVERTER": "org.apache.kafka.connect.json.JsonConverter",
                    "VALUE_CONVERTER": "org.apache.kafka.connect.json.JsonConverter",
                    "INTERNAL_KEY_CONVERTER": "org.apache.kafka.connect.json.JsonConverter",
                    "INTERNAL_VALUE_CONVERTER": "org.apache.kafka.connect.json.JsonConverter",
                    "INTERNAL_KEY_CONVERTER_SCHEMAS_ENABLE": "false",
                    "INTERNAL_VALUE_CONVERTER_SCHEMAS_ENABLE": "false",
                },
                "depends_on": [f"kafka-{i}" for i in range(kafka.num_brokers)],
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate_config_loader_service(project: Project):
        return {
            "config-loader": {
                "container_name": f"{project.name}__kafka_connect_config_loader".replace(
                    "-", "_"
                ),
                "image": "python:3.9-slim",
                "volumes": [
                    f"./kafka_connect/configs:/configs",
                    f"./kafka_connect/api.py:/app.py",
                ],
                "depends_on": ["kafka-connect"],
                "networks": [f"{project.name}_network"],
                "command": '''sh -c "sleep 30 && pip install requests && python app.py /configs"''',
            }
        }

    @staticmethod
    def generate(project: Project, kafka: Kafka, sources: List[Source]):
        psql_sources = [source for source in sources if isinstance(source, Postgres)]
        s3_source = [source for source in sources if isinstance(source, S3)][0]
        KafkaConnectService.generate_debezium_configs(
            psql_sources,
            Path(f"{project.name}/kafka_connect/configs"),
        )
        KafkaConnectService.generate_s3sink_configs(
            psql_sources, s3_source, Path(f"{project.name}/kafka_connect/configs")
        )
        download_and_extract_archive(
            "https://github.com/ClickHouse/clickhouse-kafka-connect/releases/download/v1.3.0/clickhouse-kafka-connect-v1.3.0.zip",
            Path(f"{project.name}/kafka_connect/plugins"),
        )
        download_and_extract_archive(
            "https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.6.5/confluentinc-kafka-connect-s3-10.6.5.zip",
            Path(f"{project.name}/kafka_connect/plugins"),
        )
        move_file(
            "src/dpd/services/kafka_connect/api.py", f"{project.name}/kafka_connect"
        )
        return KafkaConnectService.generate_docker_service(project, kafka)

    @staticmethod
    def generate_debezium_configs(sources: List[Postgres], target_path: Path):
        for source in sources:
            dbz_conf = {
                "name": f"dbz_{source.name}",
                "config": {
                    "name": f"dbz_{source.name}",
                    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": "false",
                    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "key.converter.schemas.enable": "false",
                    "tasks.max": "1",
                    "slot.name": "debezium_slot",
                    "publication.name": "debezium",
                    "tombstones.on.delete": "false",
                    "decimal.handling.mode": "double",
                    "replica.identity.autoset.values": "*.*:FULL",
                    "database.hostname": source.name,
                    "database.port": 5432,
                    "database.user": env_manager.get_secret(source.name, "user"),
                    "database.password": env_manager.get_secret(
                        source.name, "password"
                    ),
                    "database.dbname": env_manager.get_secret(source.name, "db"),
                    "topic.prefix": source.name,
                    "time.precision.mode": "connect",
                    "plugin.name": "pgoutput",
                    "snapshot.mode": "never",
                },
            }
            os.makedirs(
                os.path.dirname(target_path / f"{source.name}_dbz_conf.json"),
                exist_ok=True,
            )
            with open(target_path / f"{source.name}_dbz_conf.json", "w") as f:
                f.write(json.dumps(dbz_conf, indent=4))

    @staticmethod
    def generate_s3sink_configs(sources: List[Postgres], s3: S3, target_path: Path):
        for source in sources:
            dbz_conf = {
                "name": f"s3sink_{source.name}",
                "config": {
                    "name": f"s3sink_{source.name}",
                    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
                    "topics.dir": "topics",
                    "flush.size": "1000",
                    "timezone": "UTC",
                    "store.url": "http://minio:9000",
                    "topics.regex": f"{source.name}.*",
                    "locale": "cu-RU",
                    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
                    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
                    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "path.format": "YYYY-MM-dd",
                    "timestamp.extractor": "Record",
                    "s3.bucket.name": "kafka-topics",
                    "aws.access.key.id": env_manager.get_secret(s3.name, "access_key"),
                    "partition.duration.ms": "86400000",
                    "aws.secret.access.key": env_manager.get_secret(
                        s3.name, "secret_key"
                    ),
                    "value.converter.schemas.enable": "false",
                    "key.converter.schemas.enable": "false",
                    "rotate.schedule.interval.ms": "30000"
                },
            }
            os.makedirs(
                os.path.dirname(target_path / f"{source.name}_s3sink_conf.json"),
                exist_ok=True,
            )
            with open(target_path / f"{source.name}_s3sink_conf.json", "w") as f:
                f.write(json.dumps(dbz_conf, indent=4))
