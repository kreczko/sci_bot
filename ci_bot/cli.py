# -*- coding: utf-8 -*-

"""Console script for ci_bot."""

import click
import yaml
import gitlab
import os
# import requests_cache
import pickle

# requests_cache.install_cache('api_cache')

from . import gitlab as gl


def get_projects(conn, cachefile='cache.pkl'):
    if not os.path.exists(cachefile):
        projects = conn.projects.list(all=True)
        projects_to_cachefile(projects, cachefile)
        return projects
    return projects_from_cachefile(cachefile)


def projects_from_cachefile(cachefile):
    with open(cachefile, 'rb') as f:
        projects = pickle.load(f)
    return projects


def projects_to_cachefile(projects, cachefile):
    with open(cachefile, 'wb') as f:
        pickle.dump(projects, f)


@click.command()
@click.option('-c', '--config', type=click.File(), default='private_config.yaml')
@click.option('-i', '--ignore-cache', default=False)
def main(config, ignore_cache, args=None):
    """Console script for ci_bot."""
    config = yaml.load(config)
    print(config)
    connection = gl.connect(config['repo'], config['API_TOKEN'])

    remote_projects = gl.get_list_of_projects(connection)
    projects = config['projects']
    found_projects = []

    print(len(remote_projects))
    for p in remote_projects:
        # print(p.path_with_namespace)
        for project in projects:
            if not p.path_with_namespace == project:
                continue
            found_projects.append(p)

    for project in found_projects:
        print('Found', project.path_with_namespace)
        mrs = gl.get_merge_requests(project)
        print('N MRs:', len(mrs))


if __name__ == "__main__":
    main()
