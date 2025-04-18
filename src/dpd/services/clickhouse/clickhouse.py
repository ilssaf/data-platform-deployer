from dpd.models import ClickHouse, Project
from dpd.generation.secret import generate_password, env_manager
from dpd.enums import ServiceType


class ClickHouseService:
    type = ServiceType.CLICKHOUSE


    @staticmethod
    def generate_secrets(ch: ClickHouse):
        env_manager.add_secret(
            ch.name, "db", ch.database.replace("-","_")
        ) if ch.database else env_manager.add_secret(
            ch.name, "db", f"{ch.name}_db".replace("-","_")
        )
        env_manager.add_secret(
            ch.name, "user", ch.username
        ) if ch.username else env_manager.add_secret(
            ch.name, "user", f"{ch.name}_admin"
        )
        env_manager.add_secret(
            ch.name, "password", ch.password
        ) if ch.password else env_manager.add_secret(
            ch.name, "password", generate_password()
        )

    @staticmethod
    def generate(project: Project, ch: ClickHouse):
        ClickHouseService.generate_secrets(ch)
        return {
            ch.name: {
                "image": "clickhouse/clickhouse-server",
                "container_name": f"{project.name}__{ch.name}".replace("-", "_"),
                "ports": [f"{ch.port or 1234}:8123", f"{ch.port or 1234 + 1}:9000"],
                "ulimits": {"nofile": {"soft": 262144, "hard": 262144}},
                "environment": {
                    "CLICKHOUSE_DB": f"${{{ch.name}__DB}}".replace("-", "_").upper(),
                    "CLICKHOUSE_USER": f"${{{ch.name}__USER}}".replace("-", "_").upper(),
                    "CLICKHOUSE_PASSWORD": f"${{{ch.name}__PASSWORD}}".replace("-", "_").upper(),
                },
                "networks": [f"{project.name}_network"],
            }
        }
