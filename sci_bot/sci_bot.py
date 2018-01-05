from os.path import dirname, join
import confluent_kafka
import json

from .kafka_helper import get_kafka_consumer, get_topics
from .logger import log

from . import backend_gitlab as gl


def process_error_msg(msg):
    if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
        # End of partition event
        log.error('%% {} [{}] reached end at offset {}\n'.format
                  (msg.topic(), msg.partition(), msg.offset()))
    elif msg.error():
        raise confluent_kafka.KafkaException(msg.error())


def process_msg(msg):
    value = msg.value()
    value = json.loads(value)
    store_msg_value(value)

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
    # TODO: when a build finishes, download metrics and output files
    # files need to be specified in config repo
    # if it is a one-off build, check what is next in line
    pass


def process_ci_event(event):
    # TODO: when a pipeline/workflow finishes, create report
    pass


def process_issue_event(event):
    # not interesting at the moment, but might in the future
    # TODO: notify people responsible for changed files/new files in specific
    # folders
    pass


def process_merge_request_event(event):
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
    # TODO: these might include bot commands!
    # process command
    # acknowledge a known command
    # ignore own messages
    pass


def process_push_event(event):
    # not interesting at the moment, but might be used later
    # TODO: to be seen
    pass


def process_tag_event(event):
    # TODO: start release validation and deploy?
    pass


def process_unknown_event(event):
    pass


def store_msg_value(msg_value):
    path = join(dirname(__file__), '..', 'data', 'ci_bot_msg_random_hash.json')
    with open(path, 'w') as f:
        json.dump(msg_value, f, indent=2)


def listen_kafka(config, timeout=5.0):
    topics = get_topics(config)
    consumer = get_kafka_consumer()
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
                process_msg(msg)
                consumer.commit(async=False)
    except KeyboardInterrupt:
        log.info('%% Aborted by user\n')
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def get_config_repo(config):
    repo = config['configuration_repository']
