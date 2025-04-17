from dpd.models import Kafka, Project
from typing import Dict, Any
import os
from pathlib import Path
import yaml
from dpd.enums import ServiceType


# akhq:
#   connections:
#     local:
#       properties:
#         bootstrap.servers: "kafka-0:9092,kafka-1:9092,kafka-2:9092"
#       connect:
#         - name: "connect"
#           url: "http://kafka-connect:8083"


class KafkaUIService:
    type = ServiceType.CLICKHOUSE

    @staticmethod
    def generate_conf_file(kafka: Kafka, target_path: Path) -> None:
        conf = {
            "akhq": {
                "connections": {
                    "kafka": {
                        "properties": {
                            "bootstrap.servers": ",".join(f"kafka-{i}:9092" for i in range(kafka.num_brokers))
                        },
                        "connect": [
                            {"name": "connect", "url": "http://kafka-connect:8083"}
                        ],
                    }
                }
            }
        }

        os.makedirs(os.path.dirname(target_path / "application.yml"), exist_ok=True)
        with open(target_path / "application.yml", "w") as f:
            yaml.dump(conf, f, sort_keys=False)

    @staticmethod
    def generate_docker_service(project: Project, kafka: Kafka) -> Dict[str, Any]:
        return {
            "akhq": {
                "image": "tchiotludo/akhq",
                "container_name": f"{project.name}__akhq".replace("-", "_"),
                "ports": ["8086:8080"],
                "volumes": ["./akhq/application.yml:/app/application.yml"],
                "depends_on": [f"kafka-{i}" for i in range(kafka.num_brokers)],
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate(project_conf: Project, kafka: Kafka) -> Dict[str, Any]:
        KafkaUIService.generate_conf_file(kafka, Path(f"{project_conf.name}/akhq"))
        return KafkaUIService.generate_docker_service(project_conf, kafka)


# if __name__ == "__main__":
#     kafka_ui = KafkaUI()
#     gen = kafka_ui.generate(Project("kafka_ui_test", "1.0", "Kafka"), Kafka(3))
#     print(yaml.dump(gen, sort_keys=False))
