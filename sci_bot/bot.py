import os
from os.path import dirname, join
import git
import confluent_kafka
import json
import yaml

import sci_bot.kafka_helper as Kafka
from .logger import log

from . import backend_gitlab as gl
from .backend import EventType


class Bot(object):


    def __init__(self, config, timeout=5.0):
        self.config = config
        self.connection = self._establish_connection()
        self.msg_queue = Kafka.consumer()
        self.topics = config['kafka_topics']
        self.timeout = timeout
        self.name = config['bot_username']
        self.tmp_dir = config.get('tmp_dir', '/tmp')

    def _establish_connection(self):
        repo_type = self.config['repo_type']
        if repo_type.lower() == 'gitlab':
            return gl.Gitlab(self.config['repo'], self.config['API_TOKEN'])
        else:
            raise ValueError('Unknown repo type "{}"'.format(repo_type))

    def run(self):
        try:
            self._listen()
        except KeyboardInterrupt:
            log.info('%% Aborted by user\n')
        finally:
            # Close down message queue to commit final offsets.
            self.msg_queue.close()

    def _listen(self):
        self.msg_queue.subscribe(self.topics)

        while True:
            msg = self.msg_queue.poll(timeout=self.timeout)
            if msg is None:
                log.debug("No messages found.")
                continue
            if msg.error():
                _process_error_msg(msg)
            else:
                self._process_msg(msg)
                self.msg_queue.commit(async=False)

    def _process_msg(self, msg):
        event = gl.Event.from_string(msg.value())
        store_event(event, self.tmp_dir)

        event_type = event.type
        action_map = {
            EventType.BUILD: self._process_build_event,
            EventType.CI: self._process_ci_event,
            EventType.ISSUE: self._process_issue_event,
            EventType.MERGE_REQUEST: self._process_merge_request_event,
            EventType.NOTE: self._process_note_event,
            EventType.PUSH: self._process_push_event,
            EventType.TAG: self._process_tag_event,
            EventType.UNKNOWN: self._process_unknown_event,
        }
        if event_type in action_map:
            action_map[event_type](event)
        else:
            self._process_unknown_event(event)

        return 0

    def _process_build_event(self, event):
        log.debug('Got build event')
        # TODO: when a build finishes, download metrics and output files
        # files need to be specified in config repo
        # if it is a one-off build, check what is next in line
        pass


    def _process_ci_event(self, event):
        log.debug('Got CI event')
        # TODO: when a pipeline/workflow finishes, create report
        pass


    def _process_issue_event(self, event):
        log.debug('Got issues event')
        # not interesting at the moment, but might in the future
        # TODO: notify people responsible for changed files/new files in specific
        # folders
        pass


    def _process_merge_request_event(self, event):
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


    def _process_note_event(self, event):
        updated_at = event['object_attributes']['updated_at']
        log.debug('Got note event ({})'.format(updated_at))
        if not self.connection.contains_mention(event, self.name):
            log.debug('Note not for me :(')
            return
        log.debug('I was mentioned, deciding what to do')
        self.connection.reply_to_issue(event, "HAL: \"I'm Afraid I Can't Do That, Dave.\"")
        # TODO: these might include bot commands!
        # process command
        # acknowledge a known command
        # ignore own messages


    def _process_push_event(self, event):
        log.debug('Got push event')
        # not interesting at the moment, but might be used later
        # TODO: to be seen
        pass


    def _process_tag_event(self, event):
        log.debug('Got tag event')
        # TODO: start release validation and deploy?
        pass


    def _process_unknown_event(self, event):
        log.debug('Got unknown event')
        pass

    @staticmethod
    def from_yaml(config_file, timeout=5.0):
        config = yaml.load(config_file)
        return Bot(config, timeout)



def listen(config, timeout=5.0):
    bot = Bot.from_yaml(config, timeout)
    bot.run()


def forward(config):
    pass


def _process_error_msg(msg):
    if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
        # End of partition event
        log.warn('%% {} [{}] reached end at offset {}\n'.format
                  (msg.topic(), msg.partition(), msg.offset()))
    elif msg.error():
        raise confluent_kafka.KafkaException(msg.error())


def store_event(event, tmp_dir):
    event_type = event.type
    path = join(tmp_dir, 'data', f'ci_bot_msg_{event_type}_random_hash.json')
    event.to_json(path)


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
