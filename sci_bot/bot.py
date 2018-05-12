import os
from os.path import dirname, join
import git
import confluent_kafka
import json
import yaml

from .kafka_helper import get_kafka_consumer
from .logger import log

from . import backend_gitlab as gl

BOT_USERNAME = None


def parse_config(config_file):
    config = yaml.load(config_file)
    log.debug(config)
    # TODO: add some checks
    # e.g. does the API token work?
    return config


def listen(config, timeout=5.0):
    global BOT_USERNAME
    config = parse_config(config)
    topics = config['kafka_topics']
    consumer = get_kafka_consumer()
    tmp_dir = config['tmp_dir']
    BOT_USERNAME = config['bot_username']
    try:
        consumer.subscribe(topics)

        while True:
            msg = consumer.poll(timeout=timeout)
            if msg is None:
                log.debug("No messages found.")
                continue
            if msg.error():
                process_error_msg(msg)
            else:
                process_msg(msg, tmp_dir)
                consumer.commit(async=False)
    except KeyboardInterrupt:
        log.info('%% Aborted by user\n')
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


def forward():
    config = parse_config(config)
    pass


def process_error_msg(msg):
    if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
        # End of partition event
        log.error('%% {} [{}] reached end at offset {}\n'.format
                  (msg.topic(), msg.partition(), msg.offset()))
    elif msg.error():
        raise confluent_kafka.KafkaException(msg.error())


def process_msg(msg, tmp_dir='/tmp'):
    value = msg.value()
    value = json.loads(value)
    store_msg(value, tmp_dir)

    if gl.is_build_event(value):
        process_build_event(value)
    elif gl.is_ci_event(value):
        process_ci_event(value)
    elif gl.is_issue_event(value):
        process_issue_event(value)
    elif gl.is_merge_request_event(value):
        process_merge_request_event(value)
    elif gl.is_note_event(value):
        process_note_event(value)
    elif gl.is_push_event(value):
        process_push_event(value)
    elif gl.is_tag_event(value):
        process_tag_event(value)
    else:
        process_unknown_event(value)

    return 0


def process_build_event(event):
    log.debug('Got build event')
    # TODO: when a build finishes, download metrics and output files
    # files need to be specified in config repo
    # if it is a one-off build, check what is next in line
    pass


def process_ci_event(event):
    log.debug('Got CI event')
    # TODO: when a pipeline/workflow finishes, create report
    pass


def process_issue_event(event):
    log.debug('Got issues event')
    # not interesting at the moment, but might in the future
    # TODO: notify people responsible for changed files/new files in specific
    # folders
    pass


def process_merge_request_event(event):
    log.debug('Got merge request event')
    # TODO:
    # 1. notify people responsible for changed files/new files in specific
    # folders & add labels (e.g. "not-tested", 'not-validated')
    # 2. Check if MR includes all the necessary information (e.g. links to an issue)
    # 3. start simple checks if not done automatically (e.g. only config/CI repo
    # needs runner, all other repos don't)
    # 4. if all successful, change label "not-tested" -> "tests-succeeded" or
    # "tests-failed" on failure
    pass


def process_note_event(event):
    log.debug('Got note event')
    if not gl.contains_mention(event, BOT_USERNAME):
        return
    log.debug('I was mentioned, deciding what to do')
    gl.reply_to(event, "HAL: \"I'm Afraid I Can't Do That, Dave.\"")
    # TODO: these might include bot commands!
    # process command
    # acknowledge a known command
    # ignore own messages


def process_push_event(event):
    log.debug('Got push event')
    # not interesting at the moment, but might be used later
    # TODO: to be seen
    pass


def process_tag_event(event):
    log.debug('Got tag event')
    # TODO: start release validation and deploy?
    pass


def process_unknown_event(event):
    log.debug('Got unknown event')
    pass


def store_msg(msg, tmp_dir):
    event_type = gl.get_event_type(msg)
    path = join(tmp_dir, 'data', f'ci_bot_msg_{event_type}_random_hash.json')
    with open(path, 'w') as f:
        json.dump(msg, f, indent=2)


def get_config_repo(repo, auth_token):
    # repo = config['configuration_repository']
    to_path = join('/tmp', 'sci_bot', 'external', 'configrepo')
    # insert auth_token
    token = "oath2:{}".format(auth_token)
    repo = repo.replace('https://', 'https://{}@'.format(token))
    if not os.path.exists(to_path):
        log.info('Cloning config repo')
        git.Repo.clone_from(repo, to_path, branch='master')
    else:
        # TODO: check if valid repo
        log.info('Config repo already present, updating')
        repo = git.Repo(to_path)
        repo.remotes.origin.fetch()
        repo.remotes.origin.pull()


def test_gitlab(config):
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


def clone_config_repo(config):
    gitlab_token = os.environ['GIT_ACCESS_TOKEN']
    config_repo = os.environ['SCI_BOT_CONFIG_REPO']
    get_config_repo(config_repo, gitlab_token)
