from dpd.models import Project, Superset
from dpd.generation.secret import generate_password


class SupersetService:
    @staticmethod
    def generate_docker_service(project: Project, superset: Superset):
        return {
            superset.name: {
                "image": "apache/superset",
                "container_name": superset.name,
                "ports": [f"{superset.port or 8088}:8088"],
                "enviroment": {
                    "ADMIN_PASSWORD": superset.password or generate_password(),
                    "ADMIN_USER": superset.username or f"{superset.name}_admin",
                },
                "depends_on": ["postgres"],  # TODO cделать верные зависимости
                "networks": [f"{project.name}_network"],
            }
        }

    @staticmethod
    def generate(project: Project, superset: Superset):
        return SupersetService.generate_docker_service(project, superset)
