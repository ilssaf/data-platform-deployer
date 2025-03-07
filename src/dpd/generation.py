from pathlib import Path
import yaml
from typing import Dict, Any
from src.dpd.services.kafka_ui.kafka_ui import KafkaUIService
from src.dpd.models import (
    Postgres,
    S3,
    Kafka,
    KafkaConnect,
    ClickHouse,
    Project,
    Config,
    BI,
    StorageConfig,
    Streaming,
    DebeziumPostgresSourceConnector,
    Superset,
)
from src.dpd.services import (
    PostgresqlService,
    MinioService,
    KafkaConnectService,
    ClickHouseService,
    SupersetService,
    KafkaService,
)
import os


class DockerComposeGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.services = {}
        self.settings = {}
        self.networks = {f"{config.project.name}_network": {"driver": "bridge"}}

    def add_service(self, name: str, service_data: Dict[str, Any]):
        self.services[name] = service_data

    def add_settings(self, settings: Dict[str, Any]):
        self.settings = self.settings | settings

    def generate(self) -> str:
        target_path = Path(f"{self.config.project.name}/docker-compose.yml")
        compose_dict = {
            "version": "3.8",
            **self.settings,
            "services": self.services,
            "networks": self.networks,
        }
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as f:
            f.write(yaml.dump(compose_dict, sort_keys=False, default_flow_style=False))
        return yaml.dump(compose_dict, sort_keys=False, default_flow_style=False)

    def process_services(self):
        for source in self.config.sources:
            if isinstance(source, Postgres):
                self.add_service(
                    source.name, PostgresqlService.generate(self.config.project, source)
                )
            elif isinstance(source, S3):
                self.add_service(
                    source.name, MinioService.generate(self.config.project, source)
                )
        if self.config.streaming.kafka:
            self.add_settings(
                KafkaService.generate_settings(
                    self.config.project, self.config.streaming.kafka
                )
            )
            for broker_id in range(self.config.streaming.kafka.num_brokers):
                self.add_service(
                    f"kafka-{broker_id}",
                    KafkaService.generate(broker_id),
                )
            self.add_service(
                "kafka-ui",
                KafkaUIService.generate(
                    self.config.project, self.config.streaming.kafka
                ),
            )
            self.add_service(
                "kafka-connect",
                KafkaConnectService.generate(
                    self.config.project, self.config.streaming.kafka
                ),
            )

        if self.config.storage.clickhouse:
            clickhouse = self.config.storage.clickhouse
            self.add_service(
                "clickhouse",
                ClickHouseService.generate(self.config.project, clickhouse),
            )

        if self.config.bi.superset:
            superset = self.config.bi.superset
            self.add_service(
                "superset", SupersetService.generate(self.config.project, superset)
            )

        # for connector in self.config.streaming.connect.connectors:
        #     if isinstance(connector, DebeziumPostgresSourceConnector):
        #         self.add_service(
        #             connector.name,
        #             {
        #                 "image": "debezium/connect",
        #                 "environment": {
        #                     "DATABASE_HOSTNAME": connector.database_hostname,
        #                     "DATABASE_PORT": str(connector.database_port),
        #                     "DATABASE_USER": connector.database_user,
        #                     "DATABASE_PASSWORD": connector.database_password,
        #                     "DATABASE_DBNAME": connector.database_dbname,
        #                     "DATABASE_SERVER_NAME": connector.database_server_name,
        #                 },
        #                 "ports": ["8084:8083"],
        #             },
        #         )


def generate_docker_compose(config: Config) -> str:
    generator = DockerComposeGenerator(config)
    generator.process_services()
    return generator.generate()
