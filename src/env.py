import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('hpotter')

# note sqlite:///:memory: can't be used, even for testing, as it
# doesn't work with threads.
db = 'sqlite:///main.db'
