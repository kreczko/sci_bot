# -*- coding: utf-8 -*-

"""Console script for sci_bot."""
import click
import yaml
import os
import pickle

from . import gitlab as gl
from .logger import log
from dotenv import load_dotenv
from .ci_bot import listen_kafka

@click.command()
@click.option('-c', '--config', type=click.File(), default='private_config.yaml')
@click.option('-i', '--ignore-cache', default=False)
@click.option('-e', '--env_file', type=click.Path(exists=True), default='.env')
def main(config, ignore_cache, env_file, args=None):
    """Console script for sci_bot."""
    # TODO: Config should come from a git repo, instructions similar to
    # gitlab runner's config.yoml
    load_dotenv(env_file)
    config = read_config(config)

    connection = gl.connect(config['repo'], config['API_TOKEN'])

    remote_projects = gl.get_list_of_projects(connection)
    projects = config['projects']
    found_projects = []

    log.debug('Found %d remote projects', len(remote_projects))
    for p in remote_projects:
        # print(p.path_with_namespace)
        for project in projects:
            if not p.path_with_namespace == project:
                continue
            found_projects.append(p)

    for project in found_projects:
        log.debug('Found %s', project.path_with_namespace)
        mrs = gl.get_merge_requests(project)
        log.debug('N MRs: %d', len(mrs))

    listen_kafka(config)


def read_config(config_file):
    config = yaml.load(config_file)
    log.debug(config)
    # TODO:some checks
    return config

def listen(topics):
    pass

if __name__ == "__main__":
    main()
