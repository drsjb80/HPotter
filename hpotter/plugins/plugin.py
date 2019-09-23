import yaml

class Plugin(yaml.YAMLObject):
    yaml_tag = u'!plugin'
    def __init__(self, name=None, setup=None, teardown=None, container=None, alt_container=None, read_only=None, detach=None, ports=None, volumes=None, environment=None, listen_address=None, listen_port=None, table=None, capture_length=None):
        self.name = name
        self.setup = setup
        self.teardown = teardown
        self.container = container
        self.alt_container = alt_container
        self.read_only = read_only
        self.detach = detach
        self.ports = ports
        self.volumes = volumes
        self.environment = environment
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.table = table
        self.capture_length = capture_length

    def __repr__(self):
        return "%s( name: %r \n setup: %r \n teardown: %r \n container: %r\n read_only: %r\n detach: %r\n ports: %r \n volumes: %r \n environment: %r \n listen_address: %r \n listen_port: %r \n table: %r \n capture_length: %r)" % (
        self.__class__.__name__, self.name, self.setup,
        self.teardown, self.container, self.read_only, self.detach,
        self.ports, self.volumes, self.environment, self.listen_address,
        self.listen_port, self.table, self.capture_length)

    def contains_volumes(self):
        return self.volumes == []

    def makeports(self):
        return { self.ports["from"] : self.ports["connect_port"]}

def read_in_plugins(container_name):
    present = False
    file = open('hpotter/plugins/plugins.yml')
    for data in yaml.load_all(Loader=yaml.FullLoader, stream=file):
        if (data["name"] == container_name):
            present = True
            return Plugin(name=data['name'], \
                          setup=data['setup'], \
                          teardown=data['teardown'], \
                          container=data['container'], \
                          alt_container=data['alt_container'], \
                          read_only=data['read_only'], \
                          detach=data['detach'], \
                          ports=data['ports'], \
                          volumes=data['volumes'], \
                          environment=data['environment'], \
                          listen_address=data['listen_address'], \
                          listen_port=data['listen_port'], \
                          table=data['table'], \
                          capture_length=data['capture_length'] )
    if (present == None):
        print("plugin definintion not present")
