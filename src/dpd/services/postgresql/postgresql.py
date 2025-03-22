from pathlib import Path
from typing import Any, Dict
from dpd.models import Postgres, Project
from dpd.generation.secret import generate_password
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
            psql_conf.name: {
                "image": "postgres:15",  # TODO: сделать возможность менять версию, пользовательский ввод
                "container_name": psql_conf.name,
                "enviroment": {
                    "POSTGRES_USER": psql_conf.username or f"{psql_conf.name}_admin",
                    "POSTGRES_PASSWORD": psql_conf.password or generate_password(),
                    "POSTGRES_DB": psql_conf.database or f"{psql_conf.name}_db",
                },
                "ports": [f"{psql_conf.port or 5432}:5432"],
                "volumes": [
                    f"{psql_conf.name}:/var/lib/postgresql/data",
                    f"./{psql_conf.name}/postgresql.conf:/etc/postgresql/postgresql.conf",
                ],
                "command": "postgres -c 'config_file=/etc/postgresql/postgresql.conf'",
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate(project_conf: Project, psql_conf: Postgres) -> Dict[str, Any]:
        PostgresqlService.generate_conf_file(
            Path(f"{project_conf.name}/{psql_conf.name}")
        )
        return PostgresqlService.generate_docker_service(project_conf, psql_conf)
