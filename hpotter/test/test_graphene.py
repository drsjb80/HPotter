import unittest

from graphene.test import Client

from hpotter.graphql.schema import schema


class TestGraphene(unittest.TestCase):
    def test_connections_create_and_delete(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_id = int(query_result['data']['connections'][num_ids - 1]['id']) + 1
        source_ip = '127.0.0.1'
        source_port = 25252
        dest_port = 22
        proto = 6
        mutation = 'mutation { createConnection(sourceIP: "' + str(source_ip) + '", sourcePort: ' + \
                   str(source_port) + ', destPort: ' + str(dest_port) + ', proto:' + str(proto) + ') { connection ' \
                   '{ id createdAt sourceIP sourcePort destPort proto } } }'
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"createConnection":
                          {"connection":
                           {"id": next_id,
                            "createdAt": result_dict['data']['createConnection']['connection']['createdAt'],
                            "sourceIP": source_ip,
                            "sourcePort": source_port,
                            "destPort": dest_port,
                            "proto": proto
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)
        mutation = "mutation { deleteConnection(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                             {"ok": True
                              }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)

    def test_connections_read(self):
        pass

    def test_connections_update(self):
        pass

########################################################################################################################
    def test_credentials_create_and_delete(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = int(query_result['data']['connections'][num_ids - 1]['id']) + 1
        source_ip = '127.0.0.1'
        source_port = 25252
        dest_port = 22
        proto = 6
        mutation = 'mutation { createConnection(sourceIP: "' + str(source_ip) + '", sourcePort: ' + \
                   str(source_port) + ', destPort: ' + str(dest_port) + ', proto:' + str(proto) + ') { connection ' \
                   '{ id createdAt sourceIP sourcePort destPort proto } } }'
        result_dict = client.execute(mutation)
        created_at = result_dict['data']['createConnection']['connection']['createdAt']
        expected_dict = {"data":
                         {"createConnection":
                          {"connection":
                           {"id": next_conn_id,
                            "createdAt": created_at,
                            "sourceIP": source_ip,
                            "sourcePort": source_port,
                            "destPort": dest_port,
                            "proto": proto
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection created

        query = ' query { credentials { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['credentials'])
        next_id = int(query_result['data']['credentials'][num_ids - 1]['id']) + 1
        username = "test_username"
        password = "test_password"
        connection_id = next_conn_id
        mutation = 'mutation { createCredential(username: "' + username + '", password: "' + password + '", ' \
                   'connectionsId:' + str(connection_id) + ') { credential { id username password connectionsId ' \
                   'connection {id createdAt sourceIP sourcePort destPort proto} } } }'
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"createCredential":
                          {"credential":
                           {"id": next_id,
                            "username": username,
                            "password": password,
                            "connectionsId": connection_id,
                            "connection":
                                {"id": str(connection_id),
                                 "createdAt": created_at,
                                 "sourceIP": source_ip,
                                 "sourcePort": source_port,
                                 "destPort": dest_port,
                                 "proto": proto
                                 }
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert credential was created using created connection
        mutation = "mutation { deleteCredential(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteCredential":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the credential
        mutation = "mutation { deleteConnection(id: " + str(next_conn_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the connection

    def test_credentials_read(self):
        pass

    def test_credentials_update(self):
        pass

########################################################################################################################
    def test_http_commands_create_and_delete(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = int(query_result['data']['connections'][num_ids - 1]['id']) + 1
        source_ip = '127.0.0.1'
        source_port = 25252
        dest_port = 80
        proto = 6
        mutation = 'mutation { createConnection(sourceIP: "' + str(source_ip) + '", sourcePort: ' + \
                   str(source_port) + ', destPort: ' + str(dest_port) + ', proto:' + str(proto) + ') { connection ' \
                   '{ id createdAt sourceIP sourcePort destPort proto } } }'
        result_dict = client.execute(mutation)
        created_at = result_dict['data']['createConnection']['connection']['createdAt']
        expected_dict = {"data":
                         {"createConnection":
                          {"connection":
                           {"id": next_conn_id,
                            "createdAt": created_at,
                            "sourceIP": source_ip,
                            "sourcePort": source_port,
                            "destPort": dest_port,
                            "proto": proto
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection created

        query = ' query { httpCommands { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['httpCommands'])
        next_id = int(query_result['data']['httpCommands'][num_ids - 1]['id']) + 1
        request = "test_request"
        connection_id = next_conn_id
        mutation = 'mutation { createHttpCommand(request: "' + request + '", connectionsId:' + str(connection_id) + \
                   ') { httpCommand { id request connectionsId connection { id createdAt sourceIP sourcePort ' \
                   'destPort proto } } } }'
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"createHttpCommand":
                          {"httpCommand":
                           {"id": next_id,
                            "request": request,
                            "connectionsId": connection_id,
                            "connection":
                            {"id": str(connection_id),
                             "createdAt": created_at,
                             "sourceIP": source_ip,
                             "sourcePort": source_port,
                             "destPort": dest_port,
                             "proto": proto
                             }
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert http command was created using created connection
        mutation = "mutation { deleteHttpCommand(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteHttpCommand":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the http command
        mutation = "mutation { deleteConnection(id: " + str(next_conn_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the connection

    def test_http_commands_read(self):
        pass

    def test_http_commands_update(self):
        pass

########################################################################################################################
    def test_shell_commands_create_and_delete(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = int(query_result['data']['connections'][num_ids - 1]['id']) + 1
        source_ip = '127.0.0.1'
        source_port = 25252
        dest_port = 80
        proto = 6
        mutation = 'mutation { createConnection(sourceIP: "' + str(source_ip) + '", sourcePort: ' + \
                   str(source_port) + ', destPort: ' + str(dest_port) + ', proto:' + str(proto) + ') { connection ' \
                   '{ id createdAt sourceIP sourcePort destPort proto } } }'
        result_dict = client.execute(mutation)
        created_at = result_dict['data']['createConnection']['connection']['createdAt']
        expected_dict = {"data":
                         {"createConnection":
                          {"connection":
                           {"id": next_conn_id,
                            "createdAt": created_at,
                            "sourceIP": source_ip,
                            "sourcePort": source_port,
                            "destPort": dest_port,
                            "proto": proto
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection created

        query = ' query { shellCommands { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['shellCommands'])
        next_id = int(query_result['data']['shellCommands'][num_ids - 1]['id']) + 1
        command = "test_command"
        connection_id = next_conn_id
        mutation = 'mutation { createShellCommand(command: "' + command + '", connectionsId:' + str(connection_id) + \
                   ') { shellCommand { id command connectionsId connection { id createdAt sourceIP sourcePort ' \
                   'destPort proto } } } }'
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"createShellCommand":
                          {"shellCommand":
                           {"id": next_id,
                            "command": command,
                            "connectionsId": connection_id,
                            "connection":
                            {"id": str(connection_id),
                             "createdAt": created_at,
                             "sourceIP": source_ip,
                             "sourcePort": source_port,
                             "destPort": dest_port,
                             "proto": proto
                             }
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert shell command was created using created connection
        mutation = "mutation { deleteShellCommand(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteShellCommand":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the shell command
        mutation = "mutation { deleteConnection(id: " + str(next_conn_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the connection

    def test_shell_commands_read(self):
        pass

    def test_shell_commands_update(self):
        pass

########################################################################################################################
    def test_sql_create(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = int(query_result['data']['connections'][num_ids - 1]['id']) + 1
        source_ip = '127.0.0.1'
        source_port = 25252
        dest_port = 80
        proto = 6
        mutation = 'mutation { createConnection(sourceIP: "' + str(source_ip) + '", sourcePort: ' + \
                   str(source_port) + ', destPort: ' + str(dest_port) + ', proto:' + str(proto) + ') { connection ' \
                   '{ id createdAt sourceIP sourcePort destPort proto } } }'
        result_dict = client.execute(mutation)
        created_at = result_dict['data']['createConnection']['connection']['createdAt']
        expected_dict = {"data":
                         {"createConnection":
                          {"connection":
                           {"id": next_conn_id,
                            "createdAt": created_at,
                            "sourceIP": source_ip,
                            "sourcePort": source_port,
                            "destPort": dest_port,
                            "proto": proto
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection created

        query = ' query { sql { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['sql'])
        next_id = int(query_result['data']['sql'][num_ids - 1]['id']) + 1
        request = "test_request"
        connection_id = next_conn_id
        mutation = 'mutation { createSql(request: "' + request + '", connectionsId:' + str(connection_id) + \
                   ') { sqlCommand { id request connectionsId connection { id createdAt sourceIP sourcePort ' \
                   'destPort proto } } } }'
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"createSql":
                          {"sqlCommand":
                           {"id": next_id,
                            "request": request,
                            "connectionsId": connection_id,
                            "connection":
                            {"id": str(connection_id),
                             "createdAt": created_at,
                             "sourceIP": source_ip,
                             "sourcePort": source_port,
                             "destPort": dest_port,
                             "proto": proto
                             }
                            }
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert http command was created using created connection
        mutation = "mutation { deleteSql(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteSql":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the http command
        mutation = "mutation { deleteConnection(id: " + str(next_conn_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the connection

    def test_sql_read(self):
        pass

    def test_sql_update(self):
        pass

