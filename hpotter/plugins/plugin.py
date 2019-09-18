import yaml

class Plugin(yaml.YAMLObject):
    yaml_tag = u'!plugin'
    def __init__(self, name=None, setup=None, teardown=None, container=None, read_only=None, detach=None, ports=None, volumes=None, listen_address=None, listen_port=None, table=None, capture_length=None):
        self.name = name
        self.setup = setup
        self.teardown = teardown
        self.container = container
        self.read_only = read_only
        self.detach = detach
        self.ports = ports
        self.volumes = volumes
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.table = table
        self.capture_length = capture_length

    def __repr__(self):
        return "%s( name=%r \n setup=%r \n teardown=%r \n container=%r\n read_only=%r\n detach=%r\n ports=%r \n volumes=%r \n listen_address=%r \n listen_port=%r \n table=%r \n capture_length=%r)" % (
        self.__class__.__name__, self.name, self.setup,
        self.teardown, self.container, self.read_only, self.detach,
        self.ports, self.volumes, self.listen_address,
        self.listen_port, self.table, self.capture_length)


def read_in_plugins(file):
    for data in yaml.load_all(Loader=yaml.FullLoader, stream=file):
        print(data)


file = open('plugins.yml')
read_in_plugins(file)
