from src.dpd.models import S3 as Minio, Project


class MinioService:
    @staticmethod
    def generate(project: Project, minio: Minio):
        return {
            "image": "minio/minio",
            "container_name": "minio",
            "ports": [f"{minio.port}:9000"],
            "environment": {
                "MINIO_ACCESS_KEY": minio.access_key,
                "MINIO_SECRET_KEY": minio.secret_key,
            },
            "volumes": [f"{minio.data_dir or 'minio_data'}:/data"],
            "networks": [f"{project.name}_network"],
        }
