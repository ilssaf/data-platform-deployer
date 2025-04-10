from pathlib import Path
import yaml
from typing import Dict, Any
from dpd.models import (
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
    Superset,
)
from dpd.services import (
    PostgresqlService,
    MinioService,
    KafkaConnectService,
    ClickHouseService,
    SupersetService,
    KafkaService,
    ReadmeService,
    KafkaUIService,
)
import os


class DPGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.services = {}
        self.settings = {}
        self.networks = {f"{config.project.name}_network": {"driver": "bridge"}}
        self.env = {}

    def add_service(self, service_data: Dict[str, Any]):
        self.services = self.services | service_data

    def add_settings(self, settings: Dict[str, Any]):
        self.settings = self.settings | settings

    def generate(self) -> str:
        target_path = Path(f"{self.config.project.name}/docker-compose.yml")
        compose_dict = {
            "version": "3.8",
            **self.settings,
            "services": self.services,
            "volumes": self._generate_volumes(self.config),
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
                    PostgresqlService.generate(self.config.project, source)
                )
            elif isinstance(source, S3):
                self.add_service(MinioService.generate(self.config.project, source))
        if self.config.streaming.kafka:
            # self.add_settings(
            #     KafkaService.generate_settings(
            #         self.config.project, self.config.streaming.kafka
            #     )
            # )
            for broker_id in range(self.config.streaming.kafka.num_brokers):
                self.add_service(
                    KafkaService.generate(
                        self.config.project, self.config.streaming.kafka, broker_id
                    ),
                )
            self.add_service(
                KafkaUIService.generate(
                    self.config.project, self.config.streaming.kafka
                ),
            )
            self.add_service(
                KafkaConnectService.generate(
                    self.config.project,
                    self.config.streaming.kafka,
                    [
                        source
                        for source in self.config.sources
                        if isinstance(source, Postgres)
                    ],
                ),
            )

        if self.config.storage.clickhouse:
            clickhouse = self.config.storage.clickhouse
            self.add_service(
                ClickHouseService.generate(self.config.project, clickhouse),
            )

        if self.config.bi.superset:
            superset = self.config.bi.superset
            self.add_service(SupersetService.generate(self.config.project, superset))

        ReadmeService.generate_file(self.config)

    def _generate_volumes(self, conf: Config) -> Dict[str, Any]:
        src_volumes = {}
        for src in conf.sources:
            src_volumes[f"{src.name}_data"] = {"driver": "local"}
        return src_volumes


def generate_docker_compose(config: Config) -> str:
    generator = DPGenerator(config)
    generator.process_services()
    return generator.generate()
