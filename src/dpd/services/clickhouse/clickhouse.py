from src.dpd.models import ClickHouse, Project


class ClickHouseService:
    @staticmethod
    def generate(project: Project, ch: ClickHouse):
        return {
            "image": "clickhouse/clickhouse-server",
            "container_name": "clickhouse",
            "ports": [f"{ch.port}:8123", f"{ch.port + 1}:9000"],
            "ulimits": {"nofile": {"soft": 262144, "hard": 262144}},
            "enviroment": [
                f"CLICKHOUSE_DB={ch.database}",
                f"CLICKHOUSE_USER={ch.username}",
                f"CLICKHOUSE_PASSWORD={ch.password}",
            ],
            "networks": [f"{project.name}_network"],
        }
