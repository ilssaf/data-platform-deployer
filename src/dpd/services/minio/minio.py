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

    @staticmethod
    def generate_minio_init(project: Project, minio: Minio):
        return {
            "minio_init": {
                "image": "minio/mc:latest",
                "container_name": f"{project.name}__minio_init".replace("-", "_"),
                "depends_on": ["minio"],
                "environment": {
                    "MINIO_ROOT_USER": f"${{{minio.name}__ACCESS_KEY}}".replace(
                        "-", "_"
                    ).upper(),
                    "MINIO_ROOT_PASSWORD": f"${{{minio.name}__SECRET_KEY}}".replace(
                        "-", "_"
                    ).upper(),
                    "BUCKET_NAME": "kafka-topics"
                },
                "entrypoint": f'''
                /bin/sh -c "
        sleep 10
        mc config host add local http://minio:9000 {env_manager.get_secret(minio.name, "access_key")} {env_manager.get_secret(minio.name, "secret_key")} 
        mc mb local/kafka-topics || echo 'Bucket already exists'
        exit 0;
      "
''',
                "networks": [f"{project.name}_network"],
            }
        }
