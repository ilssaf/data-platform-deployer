from dpd.models import S3 as Minio, Project
from dpd.generation.secret import generate_password
from dpd.enums import ServiceType
from dpd.generation.secret import env_manager


class MinioService:
    type = ServiceType.MINIO

    @staticmethod
    def generate_secrets(minio: Minio):
        env_manager.create_secret(minio.name, "access_key")
        env_manager.create_secret(minio.name, "secret_key", 32)

    @staticmethod
    def generate(project: Project, minio: Minio):
        MinioService.generate_secrets(minio)
        return {
            "minio": {
                "image": "minio/minio",
                "container_name": f"{project.name}__minio".replace("-", "_"),
                "ports": ["9000:9000", f"{minio.port or 9001}:9001"],
                "environment": {
                    "MINIO_ROOT_USER": f"${{{minio.name}__ACCESS_KEY}}".replace(
                        "-", "_"
                    ).upper(),
                    "MINIO_ROOT_PASSWORD": f"${{{minio.name}__SECRET_KEY}}".replace(
                        "-", "_"
                    ).upper(),
                },
                "volumes": [f"{minio.name}_data:/data"],
                "command": f"minio server --console-address :{minio.port or 9001}  /data",
                "networks": [f"{project.name}_network"],
            }
        }
