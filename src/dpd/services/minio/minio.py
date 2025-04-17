from dpd.models import S3 as Minio, Project
from dpd.generation.secret import generate_password
from dpd.enums import ServiceType


class MinioService:
    type = ServiceType.MINIO

    @staticmethod
    def generate(project: Project, minio: Minio):
        return {
            "minio": {
                "image": "minio/minio",
                "container_name": f"{project.name}__minio".replace("-", "_"),
                "ports": [f"{minio.port or 9000}:9000"],
                "environment": {
                    "MINIO_ACCESS_KEY": minio.access_key or generate_password(16),
                    "MINIO_SECRET_KEY": minio.secret_key or generate_password(32),
                },
                "volumes": [f"{minio.name}_data:/data"],
                "command": "minio server /data",
                "networks": [f"{project.name}_network"],
            }
        }
