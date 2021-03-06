from __future__ import print_function
import os
import sys
import confluent_kafka


def get_config():
    config = {
        'bootstrap.servers': os.environ['KAFKA_BROKERS'],
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'},
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': os.environ['KAFKA_USERNAME'],
        'sasl.password': os.environ['KAFKA_PASSWORD'],
        'group.id': 'bot',
    }
    return config


def get_kafka_producer():
    producer = None
    try:
        producer = confluent_kafka.Producer(**get_config())
    except Exception as e:
        print('Could not create kafka producer', e, file=sys.stderr)
    return producer


def get_kafka_consumer():
    consumer = None
    try:
        consumer = confluent_kafka.Consumer(**get_config())
    except Exception as e:
        print('Could not create kafka consumer', e, file=sys.stderr)
    return consumer

def get_topics(config):
    prefix = os.environ['KAFKA_TOPIC_PREFIX']
    topics = config['kafka_topics']
    topics = [prefix + t for t in topics]
    return topics
