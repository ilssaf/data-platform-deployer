from pathlib import Path
from typing import Any, Dict
from dpd.models import Postgres, Project
from dpd.generation.secret import generate_password
import shutil
import os

from dpd.enums import ServiceType
from dpd.generation.port_manager import port_manager
from dpd.generation.secret import env_manager


class PostgresqlService:
    type = ServiceType.POSTGRESQL

    @staticmethod
    def generate_conf_file(target_path: Path) -> None:
        os.makedirs(os.path.dirname(target_path / "postgresql.conf"), exist_ok=True)
        shutil.copyfile(
            "src/dpd/services/postgresql/postgresql.conf",
            target_path / "postgresql.conf",
        )

    @staticmethod
    def generate_init_sql_script(target_path: Path) -> None:
        sql_content = """
-- Auto-generated initialization script for PostgreSQL
-- Creates Debezium publication for all tables in public schema

CREATE PUBLICATION debezium FOR TABLES IN SCHEMA public;

-- Optional: Uncomment to grant required privileges if using separate user
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;
"""
        with open(target_path / "init.sql", "w") as f:
            f.write(sql_content)

    @staticmethod
    def generate_secrets(psql_conf: Postgres):
        env_manager.add_secret(
            psql_conf.name, "db", psql_conf.database
        ) if psql_conf.database else env_manager.add_secret(
            psql_conf.name, "db", f"{psql_conf.name}_db"
        )
        env_manager.add_secret(
            psql_conf.name, "user", psql_conf.username
        ) if psql_conf.username else env_manager.add_secret(
            psql_conf.name, "user", f"{psql_conf.name}_admin"
        )
        env_manager.add_secret(
            psql_conf.name, "password", psql_conf.password
        ) if psql_conf.password else env_manager.add_secret(
            psql_conf.name, "password", generate_password()
        )

    @staticmethod
    def generate_docker_service(
        project: Project, psql_conf: Postgres
    ) -> Dict[str, Any]:
        PostgresqlService.generate_secrets(psql_conf)
        return {
            psql_conf.name: {
                "image": "postgres:15",
                "container_name": f"{project.name}__{psql_conf.name}".replace("-", "_"),
                "environment": {
                    "POSTGRES_USER": f"${{{psql_conf.name}__USER}}".replace(
                        "-", "_"
                    ).upper(),
                    "POSTGRES_PASSWORD": f"${{{psql_conf.name}__PASSWORD}}".replace(
                        "-", "_"
                    ).upper(),
                    "POSTGRES_DB": f"${{{psql_conf.name}__DB}}".replace(
                        "-", "_"
                    ).upper(),
                },
                "ports": [
                    f"{port_manager.add_port(psql_conf.name, PostgresqlService.type)}:5432"
                ],
                "volumes": [
                    f"{psql_conf.name}_data:/var/lib/postgresql/data",
                    f"./{psql_conf.name}/postgresql.conf:/etc/postgresql/postgresql.conf",
                    f"./{psql_conf.name}/init.sql:/docker-entrypoint-initdb.d/init.sql",
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
        PostgresqlService.generate_init_sql_script(
            Path(f"{project_conf.name}/{psql_conf.name}")
        )
        return PostgresqlService.generate_docker_service(project_conf, psql_conf)
