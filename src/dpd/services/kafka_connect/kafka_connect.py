from src.dpd.models import Kafka, Project


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
    def generate(project: Project, kafka: Kafka):
        return KafkaConnectService.generate_docker_service(project, kafka)
