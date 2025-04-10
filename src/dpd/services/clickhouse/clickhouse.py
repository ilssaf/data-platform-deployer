from dpd.models import ClickHouse, Project
from dpd.generation.secret import generate_password


class ClickHouseService:
    @staticmethod
    def generate(project: Project, ch: ClickHouse):
        return {
            "clickhouse": {
                "image": "clickhouse/clickhouse-server",
                "container_name": ch.name,
                "ports": [f"{ch.port}:8123", f"{ch.port + 1}:9000"],
                "ulimits": {"nofile": {"soft": 262144, "hard": 262144}},
                "environment": [
                    f"CLICKHOUSE_DB={ch.database or f'{ch.name}_db'}",
                    f"CLICKHOUSE_USER={ch.username or f'{ch.name}_admin'}",
                    f"CLICKHOUSE_PASSWORD={ch.password or generate_password()}",
                ],
                "networks": [f"{project.name}_network"],
            }
        }
