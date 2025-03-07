from dpd.models import load_config_from_json
from dpd.generation import DockerComposeGenerator
import click


@click.group()
def main():
    """Data Platform Deployer CLI"""
    pass


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to the configuration file (JSON).",
)
def generate(config):
    """Generate configuration files for the data platform"""
    if config:
        click.echo(f"Generating configurations from {config}...")
        gen = DockerComposeGenerator(load_config_from_json(config))
        gen.process_services()
        gen.generate()

    else:
        click.echo("No configuration file provided. Using defaults...")


@click.command()
def cleanup():
    """Clean up deployed resources"""
    click.echo("Cleaning up resources...")


main.add_command(generate)
main.add_command(cleanup)

if __name__ == "__main__":
    main()
