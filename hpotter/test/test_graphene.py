import unittest

from graphene.test import Client

from hpotter.graphql.schema import schema


class TestGraphene(unittest.TestCase):
    def test_connections_read(self):
        client = Client(schema=schema)
        query = ' query { connection(sourceIP: "127.0.0.1", destPort: 22, proto: 6) { ' \
                'id createdAt sourceIP sourcePort destPort proto} }'
        query_result = client.execute(query)
        self.assertEqual("127.0.0.1", query_result['data']['connection']['sourceIP'])
        self.assertEqual(22, query_result['data']['connection']['destPort'])
        self.assertEqual(6, query_result['data']['connection']['proto'])

    def test_connections_cud(self):
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
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection was created

        mutation = 'mutation { updateConnection(id: ' + str(next_id) + ', sourceIP: "7.7.7.7", sourcePort: 22,' \
                   ' destPort: 53, proto:' + str(proto) + ') { connection { id createdAt sourceIP sourcePort ' \
                   'destPort proto } } }'
        result_dict = client.execute(mutation)
        # Assert the connection was updated
        self.assertEqual("7.7.7.7", result_dict['data']['updateConnection']['connection']['sourceIP'])
        self.assertEqual(22, result_dict['data']['updateConnection']['connection']['sourcePort'])
        self.assertEqual(53, result_dict['data']['updateConnection']['connection']['destPort'])

        mutation = "mutation { deleteConnection(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert connection was deleted

    def test_credentials_read(self):
        client = Client(schema=schema)
        query = ' query { credential(username: "root", password: "root") { ' \
                'id username password connectionsId} }'
        query_result = client.execute(query)
        self.assertEqual("root", query_result['data']['credential']['username'])
        self.assertEqual("root", query_result['data']['credential']['password'])

    def test_credentials_cud(self):
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
        mutation = 'mutation { updateCredential(id: ' + str(next_id) + ', username: "updated username", ' \
                   'password: "updated password", connectionsId: 5) { credential { id username password ' \
                   'connectionsId connection {id createdAt sourceIP sourcePort destPort proto} } } }'
        result_dict = client.execute(mutation)
        # Assert credential was updated
        self.assertEqual("updated username", result_dict['data']['updateCredential']['credential']['username'])
        self.assertEqual("updated password", result_dict['data']['updateCredential']['credential']['password'])
        self.assertEqual(5, result_dict['data']['updateCredential']['credential']['connectionsId'])

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

    def test_http_commands_read(self):
        client = Client(schema=schema)
        query = ' query { httpCommand(request: "POST /linuxse.php HTTP/1.1\\r\\nContent-Type: ' \
                'application/x-www-form-urlencoded\\r\\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; ' \
                'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/' \
                '537.36\\r\\nHost: 174.29.34.155\\r\\nContent-Length: 24\\r\\nConnection: Keep-Alive\\r\\n' \
                'Cache-Control: no-cache\\r\\n\\r\\nzuo=die(@md5(J4nur4ry));") { id request ' \
                'connectionsId connection { id createdAt sourceIP ' \
                'sourcePort destPort proto}} }'
        query_result = client.execute(query)
        self.assertEqual("POST /linuxse.php HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded"
                         "\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36\r\nHost: 174.29.34.155"
                         "\r\nContent-Length: 24\r\nConnection: Keep-Alive\r\nCache-Control: "
                         "no-cache\r\n\r\nzuo=die(@md5(J4nur4ry));",
                         query_result['data']['httpCommand']['request'])

    def test_http_commands_cud(self):
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

        mutation = 'mutation { updateHttpCommand(id: ' + str(next_id) + 'request: "updated_request", ' \
                   'connectionsId: 5) { httpCommand { id request connectionsId connection { id createdAt ' \
                   'sourceIP sourcePort destPort proto } } } }'
        result_dict = client.execute(mutation)
        # Assert http command was updated
        self.assertEqual("updated_request", result_dict['data']['updateHttpCommand']['httpCommand']['request'])
        self.assertEqual(5, result_dict['data']['updateHttpCommand']['httpCommand']['connectionsId'])

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

    def test_shell_commands_read(self):
        client = Client(schema=schema)
        query = ' query { shellCommand(command: "shell") { id command connectionsId connection { id createdAt ' \
                'sourceIP sourcePort destPort proto}} }'
        query_result = client.execute(query)
        self.assertEqual("shell", query_result['data']['shellCommand']['command'])

    def test_shell_commands_cud(self):
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

        mutation = 'mutation { updateShellCommand(id: ' + str(next_id) + ', command: "updated shell command", ' \
                   'connectionsId: 5) { shellCommand { id command connectionsId connection { id createdAt sourceIP ' \
                   'sourcePort destPort proto } } } }'
        result_dict = client.execute(mutation)
        # Assert shell command was updated
        self.assertEqual("updated shell command", result_dict['data']['updateShellCommand']['shellCommand']['command'])
        self.assertEqual(5, result_dict['data']['updateShellCommand']['shellCommand']['connectionsId'])

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

    def test_sql_read(self):
        client = Client(schema=schema)
        query = ' query { sqlQuery (request: "\' OR 1=1") { id request connectionsId } }'
        query_result = client.execute(query)
        self.assertEqual("' OR 1=1", query_result['data']['sqlQuery']['request'])

    def test_sql_cud(self):
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

        query = ' query { sqlQueries { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['sqlQueries'])
        next_id = int(query_result['data']['sqlQueries'][num_ids - 1]['id']) + 1
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
        self.assertDictEqual(result_dict, expected_dict)  # Assert sql query was created using created connection

        mutation = 'mutation { updateSql(id: ' + str(next_id) + ', request: "updated sql request", connectionsId: 5)' \
                   ' { sql { id request connectionsId connection { id createdAt sourceIP sourcePort destPort' \
                   ' proto } } } }'
        result_dict = client.execute(mutation)
        # Assert sql command was updated
        self.assertEqual("updated sql request", result_dict['data']['updateSql']['sql']['request'])
        self.assertEqual(5, result_dict['data']['updateSql']['sql']['connectionsId'])
        mutation = "mutation { deleteSql(id: " + str(next_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteSql":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the sql query
        mutation = "mutation { deleteConnection(id: " + str(next_conn_id) + ") { ok } }"
        result_dict = client.execute(mutation)
        expected_dict = {"data":
                         {"deleteConnection":
                          {"ok": True
                           }
                          }
                         }
        self.assertDictEqual(result_dict, expected_dict)  # Assert deletion of the connection
