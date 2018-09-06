import logging
import logging.config

logging.config.fileConfig('hpotter/logging.conf')
logger = logging.getLogger('hpotter')

# note sqlite:///:memory: can't be used, even for testing, as it
# doesn't work with threads.
db = 'sqlite:///main.db'

jsonserverport = 8000
