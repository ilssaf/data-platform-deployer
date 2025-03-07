from src.dpd.models import Project, Superset


class SupersetService:
    @staticmethod
    def generate_docker_service(project: Project, superset: Superset):
        return {
            "image": "apache/superset",
            "container_name": "superset",
            "ports": [f"{superset.port}:8088"],
            "enviroment": [
                f"ADMIN_PASSWORD={superset.password}",
                f"ADMIN_USER={superset.username}",
            ],
            "depends_on": ["postgres"],
            "networks": [f"{project.name}_network"],
        }

    @staticmethod
    def generate(project: Project, superset: Superset):
        return SupersetService.generate_docker_service(project, superset)
