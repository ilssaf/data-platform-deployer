from src.dpd.models import load_config_from_json
from src.dpd.generation import DockerComposeGenerator


if __name__ == "__main__":
    config = load_config_from_json("examples/test.json")
    gen = DockerComposeGenerator(config)
    gen.process_services()
    print(gen.generate())
