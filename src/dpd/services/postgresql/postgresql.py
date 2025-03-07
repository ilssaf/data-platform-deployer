from pathlib import Path
from typing import Any, Dict
from src.dpd.models import Postgres, Project
import shutil
import os


class PostgresqlService:
    @staticmethod
    def generate_conf_file(target_path: Path) -> None:
        os.makedirs(os.path.dirname(target_path / "postgresql.conf"), exist_ok=True)
        shutil.copyfile(
            "src/dpd/services/postgresql/postgresql.conf",
            target_path / "postgresql.conf",
        )

    @staticmethod
    def generate_docker_service(
        project: Project, psql_conf: Postgres
    ) -> Dict[str, Any]:
        return {
            psql_conf.host: {
                "image": "postgres:15",  # TODO: сделать возможность менять версию, пользовательский ввод
                "container_name": psql_conf.host,
                "enviroment": {
                    "POSTGRES_USER": psql_conf.username,
                    "POSTGRES_PASSWORD": psql_conf.password,
                    "POSTGRES_DB": psql_conf.database,
                },
                "ports": [f"{psql_conf.port}:5432"],
                "volumes": [
                    f"{psql_conf.host}:/var/lib/postgresql/data",
                    f"./{psql_conf.host}/postgresql.conf:/etc/postgresql/postgresql.conf",
                ],
                "command": "postgres -c 'config_file=/etc/postgresql/postgresql.conf'",
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate(project_conf: Project, psql_conf: Postgres) -> Dict[str, Any]:
        PostgresqlService.generate_conf_file(
            Path(f"{project_conf.name}/{psql_conf.host}")
        )
        return PostgresqlService.generate_docker_service(project_conf, psql_conf)
