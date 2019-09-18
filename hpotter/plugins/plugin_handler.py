#httpipe, mariadb, 

import os
import platform
import docker
import re

from hpotter.tables import SQL, SQL_COMMAND_LENGTH
from hpotter.env import logger
from hpotter.plugins.generic import PipeThread

class Singletons():
    current_container = None
    current_thread = None

def rm_container():

def start_server():

def stop_server():
