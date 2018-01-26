"""Logging configuration for ci_bot package."""
import os
import logging

debug = os.environ.get('DEBUG', False)

log = logging.getLogger('sci_bot')
if debug:
    log.setLevel(logging.DEBUG)

# add loggers
ch = logging.StreamHandler()
if not debug:
    ch.setLevel(logging.WARNING)
else:
    ch.setLevel(logging.DEBUG)
# log format
formatter = logging.Formatter(
    '%(asctime)s [%(name)s]  %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
