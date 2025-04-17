from dpd.models import Kafka, Project
from typing import Dict, Any
from dpd.enums import ServiceType


class KafkaService:
    type = ServiceType.KAFKA

    @staticmethod
    def generate_settings(project: Project, kafka_conf: Kafka) -> Dict[str, Any]:
        return {
            "kafka-common": {
                "image": "bitname/kafka:latest",
                "ports": ["9092"],
                "healthcheck": {
                    "test": "bash -c printf  > /dev/tcp/127.0.0.1/9092; exit $$?;",
                    "interval": "5s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s",
                },
                "restart": "unless-stopped",
                "networks": [f"{project.name}_network"],
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
    def generate(
        project: Project, kafka_conf: Kafka, broker_id: int
    ) -> Dict[str, Any]:
        return {
            f"kafka-{broker_id}": {
                "container_name": f"{project.name}__kafka-{broker_id}".replace("-","_"),
                "image": "bitnami/kafka:latest",
                "ports": ["9092"],
                "healthcheck": {
                    "test": 'bash -c printf "" > /dev/tcp/127.0.0.1/9092; exit $$?;',
                    "interval": "5s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s",
                },
                "restart": "unless-stopped",
                "networks": [f"{project.name}_network"],
                "environment": {
                    "ALLOW_PLAINTEXT_LISTENER": "yes",
                    "KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE": "true",
                    "KAFKA_CFG_CONTROLLER_QUORUM_VOTERS": ",".join(
                        f"{i}@kafka-{i}:9093" for i in range(kafka_conf.num_brokers)
                    ),
                    "KAFKA_KRAFT_CLUSTER_ID": "abcdefghijklmnopqrstuv",
                    "KAFKA_CFG_PROCESS_ROLES": "controller,broker",
                    "KAFKA_CFG_CONTROLLER_LISTENER_NAMES": "CONTROLLER",
                    "KAFKA_CFG_LISTENERS": "PLAINTEXT://:9092,CONTROLLER://:9093",
                    "KAFKA_CFG_NODE_ID": broker_id,
                },
            }
        }


# Вывод результата
# yaml.dump(data, print)

# Вывод результата
# yaml.dump(data, print)

# kafka_service = KafkaService()
# settings = kafka_service.generate_settings(Project("kafka", "1.0", "Kafka"), Kafka(3))
# print(yaml.dump(settings, sort_keys=False))
# gen = kafka_service.generate(Kafka(3))
# # print(gen)
# print(yaml.dump(gen, sort_keys=False))
