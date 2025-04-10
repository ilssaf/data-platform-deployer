from dpd.models import S3 as Minio, Project
from dpd.generation.secret import generate_password


class MinioService:
    @staticmethod
    def generate(project: Project, minio: Minio):
        return {
            "minio": {
                "image": "minio/minio",
                "container_name": "minio",
                "ports": [f"{minio.port or 9001}:9000"],
                "environment": {
                    "MINIO_ACCESS_KEY": minio.access_key or generate_password(16),
                    "MINIO_SECRET_KEY": minio.secret_key or generate_password(32),
                },
                "volumes": [f"{minio.name}_data:/data"],
                "networks": [f"{project.name}_network"],
            }
        }
