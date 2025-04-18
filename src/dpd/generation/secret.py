import string
import secrets

from typing import Dict
from dpd.models import Config


def generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(length))
    return password


class EnvManager:
    def __init__(self):
        self.__services2secrets: Dict[str, Dict[str, str]] = {}

    def generate_env_file(self, conf: Config) -> None:
        env = ""
        for service, service_sercets in self.__services2secrets.items():
            env += f"# Enviroment Variables for service {service}\n"
            for k, v in service_sercets.items():
                env += f"{service}__{k}".replace("-", "_").upper() + f"={v}\n"

        with open(f"{conf.project.name}/.env", "w") as f:
            f.write(env)

    def create_secret(self, service_name: str, key: str, secret_length=16) -> str:
        secret = generate_password(secret_length)
        if service_name not in self.__services2secrets.keys():
            self.__services2secrets[service_name] = {}
        self.__services2secrets[service_name][key] = secret

    def add_secret(self, service_name: str, key: str, secret: str):
        if service_name not in self.__services2secrets.keys():
            self.__services2secrets[service_name] = {}
        self.__services2secrets[service_name][key] = secret

    def get_secret(self, service_id: str, key: str) -> str:
        if service_id not in self.__services2secrets:
            return ""
        if key not in self.__services2secrets[service_id]:
            return ""
        return self.__services2secrets[service_id][key]


env_manager = EnvManager()
