import confluent_kafka
import json

from .kafka_helper import get_kafka_consumer, get_topics
from .logger import log


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
    log.debug(str(value))

    return 0


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
