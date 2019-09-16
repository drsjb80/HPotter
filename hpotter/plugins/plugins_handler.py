import yaml

class Plugin(yaml.YAMLObject):
    yaml_tag = u'!plugin'
    def __init__(self):
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


with open('test_yaml.yml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    print(data.name)
    print(data.ports['from'])
    print(data.volumes['apache2']['bind'])
    print(data.table)
