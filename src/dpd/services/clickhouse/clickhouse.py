from dpd.models import ClickHouse, Project
from dpd.generation.secret import generate_password
from dpd.enums import ServiceType


class ClickHouseService:
    type = ServiceType.CLICKHOUSE

    @staticmethod
    def generate(project: Project, ch: ClickHouse):
        return {
            ch.name: {
                "image": "clickhouse/clickhouse-server",
                "container_name": f"{project.name}__{ch.name}".replace("-", "_"),
                "ports": [f"{ch.port or 1234}:8123", f"{ch.port or 1234 + 1}:9000"],
                "ulimits": {"nofile": {"soft": 262144, "hard": 262144}},
                "environment": [
                    f"CLICKHOUSE_DB={ch.database or f'{ch.name}_db'}",
                    f"CLICKHOUSE_USER={ch.username or f'{ch.name}_admin'}",
                    f"CLICKHOUSE_PASSWORD={ch.password or generate_password()}",
                ],
                "networks": [f"{project.name}_network"],
            }
        }
