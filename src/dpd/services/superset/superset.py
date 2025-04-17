from dpd.models import Project, Config, Superset
from dpd.generation.secret import generate_password
from dpd.enums import ServiceType


class SupersetService:
    type = ServiceType.SUPERSET

    @staticmethod
    def generate_docker_service(config: Config, superset: Superset):
        return {
            superset.name: {
                "image": "apache/superset",
                "container_name": f"{config.project.name}__{superset.name}".replace("-","_"),
                "ports": [f"{superset.port or 8088}:8088"],
                "environment": {"SUPERSET_SECRET_KEY": generate_password(24)},
                "command": f"""
        sh -c "
        superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@admin.com --password {generate_password()} &&
        superset db upgrade &&
        superset init &&
        superset run -p 8088 --host=0.0.0.0 --with-threads --reload --debugger
        "
""",
                "depends_on": [config.storage.clickhouse.name],
                "networks": [f"{config.project.name}_network"],
            }
        }

    @staticmethod
    def generate(config: Config):
        return SupersetService.generate_docker_service(config, config.bi.superset)
