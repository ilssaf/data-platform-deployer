from pathlib import Path
from dpd.models import Postgres, Kafka, Project
from typing import List
import os
import json


class KafkaConnectService:
    @staticmethod
    def generate_docker_service(project: Project, kafka: Kafka):
        return {
            "kafka-connect": {
                "container_name": "kafka-connect",
                "image": "debezium/connect:3.0.0.Final",
                "ports": ["8083:8083"],
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
    def generate(project: Project, kafka: Kafka, sources: List[Postgres]):
        KafkaConnectService.generate_debezium_configs(
            sources,
            Path(f"{project.name}/kafka_connect"),
        )
        return KafkaConnectService.generate_docker_service(project, kafka)

    @staticmethod
    def generate_debezium_configs(sources: List[Postgres], target_path: Path):
        for source in sources:
            dbz_conf = {
                "name": source.name,
                "config": {
                    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                    "tasks.max": "1",
                    "slot.name": f"{source.name}_slot",
                    "database.hostname": "<hostname>",
                    "database.port": "<port>",
                    "database.user": "<username>",
                    "database.password": source.password,
                    "database.dbname": source.database,
                    "database.server.name": source.name,
                    "topic.prefix": source.name,
                    "schema.include.list": "public",
                    "table.include.list": "public.*",
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
