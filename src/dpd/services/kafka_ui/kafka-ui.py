from turtle import st
from src.dpd.models import Kafka, Project
from typing import Dict, Any
import os
from pathlib import Path
import yaml


class KafkaUIService:
    @staticmethod
    def generate_conf_file(kafka: Kafka, target_path: Path) -> None:
        conf = {
            "auth": {"type": "LOGIN_FORM"},
            "spring": {"security": {"user": {"name": "admin", "password": "admin"}}},
            "kafka": {
                "clusters": [
                    {
                        "bootstrapServers": ",".join(
                            f"kafka-{i}:9092" for i in range(kafka.num_brokers)
                        ),
                        "kafkaConnect": [
                            {
                                "address": "http://kafka-connect:8083",
                                "name": "kafka-connect",
                            }
                        ],
                        # "metrics": {"port": 9404, "type": "PROMETHEUS"}, // TODO: сделать если будет графана + прометеус
                        "name": "kafka",
                        "properties": {},
                        "readOnly": False,
                    }
                ]
            },
            "rbac": {"roles": []},
            "webclient": {},
        }

        os.makedirs(os.path.dirname(target_path / "config.yml"), exist_ok=True)
        with open(target_path / "config.yml", "w") as f:
            yaml.dump(conf, f)

    @staticmethod
    def generate_docker_service(project: Project, kafka: Kafka) -> Dict[str, Any]:
        return {
            "kafka-ui": {
                "image": "image: provectuslabs/kafka-ui:latest",
                "container_name": "kafka-ui",
                "ports": ["8080:8080"],
                "volumes": [".kafka-ui/config.yml:/etc/kafkaui/dynamic_config.yaml"],
                "depends_on": [f"kafka-{i}" for i in range(kafka.num_brokers)],
                "environment": {
                    "DYNAMIC_CONFIG_ENABLED": "true",
                },
                "healthcheck": {
                    "test": "wget --no-verbose --tries=1 --spider localhost:8080 || exit 1",
                    "interval": "5s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s",
                },
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate(project_conf: Project, kafka: Kafka) -> Dict[str, Any]:
        KafkaUIService._generate_conf_file(kafka, Path(f"{project_conf.name}/kafka-ui"))
        return KafkaUIService._generate_docker_service(kafka)


# if __name__ == "__main__":
#     kafka_ui = KafkaUI()
#     gen = kafka_ui.generate(Project("kafka_ui_test", "1.0", "Kafka"), Kafka(3))
#     print(yaml.dump(gen, sort_keys=False))
