from dpd.models import load_config_from_file, validate
from dpd.generation.data_platform import DPGenerator
import click
import os


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
        click.echo("💡 Validating configuration file...")
        if validate(
            config, os.path.join(os.path.dirname(__file__), "schema.json")
        ):
            click.echo("💡 Configuration file is valid.")
            conf = load_config_from_file(config)
            dp = DPGenerator(conf)
            click.echo("🚀 Generating configuration files...")
            dp.process_services()
            dp.generate()
            click.echo("🚀 Configuration files generated.")

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
