from pathlib import Path
from dpd.models import Postgres, Kafka, Project
from typing import List
import os
import json
from dpd.enums import ServiceType

from dpd.generation.secret import env_manager


class KafkaConnectService:
    type = ServiceType.KAFKA_CONNECT

    @staticmethod
    def generate_docker_service(project: Project, kafka: Kafka):
        return {
            "kafka-connect": {
                "container_name": f"{project.name}__kafka_connect".replace("-", "_"),
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
