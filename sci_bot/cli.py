# -*- coding: utf-8 -*-

"""Console script for sci_bot."""
import click
import sys

from dotenv import load_dotenv
from sci_bot import bot


@click.command()
@click.option('-c', '--config', type=click.File(), default='private_config.yaml')
@click.option('-i', '--ignore-cache', default=False)
@click.option('-e', '--env_file', type=click.Path(exists=True), default='.env')
@click.option('--listen', help='Listens to the work queue', is_flag=True)
@click.option('--forward', help='Forwards webhook to the work queue', is_flag=True)
def main(config, ignore_cache, env_file, listen, forward):
    """Console script for sci_bot."""
    # TODO: Config should come from a git repo, instructions similar to
    # gitlab runner's config.yoml
    load_dotenv(env_file)
    import os
    print(os.environ['KAFKA_BROKERS'], os.environ['KAFKA_USERNAME'], os.environ['KAFKA_PASSWORD'])

    if listen and forward:
        sys.exit('Cannot listen and forward at the same time')

    if listen:
        bot.listen(config)

    if forward:
        bot.forward(config)

    # sci_bot.test_gitlab(config)
    # sci_bot.clone_config_repo(config)


if __name__ == "__main__":
    main()
