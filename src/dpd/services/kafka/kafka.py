from src.dpd.models import Kafka, Project
from typing import Dict, Any


class KafkaService:
    @staticmethod
    def generate_settings(project_conf: Project, kafka_conf: Kafka) -> Dict[str, Any]:
        return {
            "kafka-common": {
                "image": "bitname/kafka:latest",
                "ports": ["9092"],
                "healthcheck": {
                    "test": [
                        "bash",
                        "-c",
                        'printf "" > /dev/tcp/127.0.0.1/9092; exit $$?;',
                    ],
                    "interval": "5s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s",
                },
                "restart": "unless-stopped",
                "networks": [f"{project_conf.name}_network"],
            },
            "kafka-env-common": {
                "ALLOW_PLAINTEXT_LISTENER": "yes",
                "KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE": "true",
                "KAFKA_CFG_CONTROLLER_QUORUM_VOTERS": ",".join(
                    f"{i}@kafka-{i}:9093" for i in range(kafka_conf.num_brokers)
                ),
                "KAFKA_KRAFT_CLUSTER_ID": "abcdefghijklmnopqrstuv",
                "KAFKA_CFG_PROCESS_ROLES": "controller,broker",
                "KAFKA_CFG_CONTROLLER_LISTENER_NAMES": "CONTROLLER",
                "KAFKA_CFG_LISTENERS": "PLAINTEXT://:9092,CONTROLLER://:9093",
                #   "EXTRA_ARGS": "\"-Xms128m -Xmx256m -javaagent:/opt/jmx-exporter/jmx_prometheus_javaagent-0.19.0.jar=9404:/opt/jmx-exporter/kafka-2_0_0.yml\"" # TODO сделать если будет графана + прометеус
            },
        }

    @staticmethod
    def generate(broker_id: int) -> Dict[str, Any]:
        return {
            f"kafka-{broker_id}": {
                "<<": "*kafka-common",
                "environment": {
                    "<<": "*kafka-env-common",
                    "KAFKA_BROKER_ID": broker_id,
                },
            }
        }


# kafka_service = KafkaService()
# settings = kafka_service.generate_settings(Project("kafka", "1.0", "Kafka"), Kafka(3))
# print(yaml.dump(settings, sort_keys=False))
# gen = kafka_service.generate(Kafka(3))
# # print(gen)
# print(yaml.dump(gen, sort_keys=False))
