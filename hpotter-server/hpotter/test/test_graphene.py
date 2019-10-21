import unittest
from hpotter.tables import check_for_tables

check_num_ids = lambda num_ids, result_dict: 1 if num_ids == 0 else int(result_dict[num_ids-1]['id']) + 1
check_for_tables()

from hpotter.graphql.schema import schema
from graphene.test import Client
        

class TestGraphene(unittest.TestCase):
    def test_connections_crud(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['connections'])
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

        query = ' query { connection(sourceIP: "' + source_ip + '", destPort: ' + str(dest_port) + ', proto: ' + \
                str(proto) + ') { id createdAt sourceIP sourcePort destPort proto} }'
        query_result = client.execute(query)
        self.assertEqual("127.0.0.1", query_result['data']['connection']['sourceIP'])  # Assert query read success
        self.assertEqual(22, query_result['data']['connection']['destPort'])  # Assert query read success
        self.assertEqual(6, query_result['data']['connection']['proto'])  # Assert query read success

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

    def test_credentials_crud(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['connections'])
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
        next_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['credentials'])
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

        query = ' query { credential(username: "' + username + '", password: "' + password + '") { ' \
                'id username password connectionsId} }'
        query_result = client.execute(query)
        self.assertEqual(username, query_result['data']['credential']['username'])  # Assert query read success
        self.assertEqual(password, query_result['data']['credential']['password'])  # Assert query read success

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

    def test_http_commands_crud(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['connections'])
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
        next_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['httpCommands'])
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

        query = ' query { httpCommand(request: "' + request + '") { id request ' \
                'connectionsId connection { id createdAt sourceIP ' \
                'sourcePort destPort proto}} }'
        query_result = client.execute(query)
        self.assertEqual(request, query_result['data']['httpCommand']['request'])  # Assert query read success

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

    def test_shell_commands_crud(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['connections'])
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
        next_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['shellCommands'])
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

        query = ' query { shellCommand(command: "' + command + '") { id command connectionsId connection { id ' \
                'createdAt sourceIP sourcePort destPort proto}} }'
        query_result = client.execute(query)
        self.assertEqual(command, query_result['data']['shellCommand']['command'])  # Assert query read successful

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

    def test_sql_crud(self):
        client = Client(schema=schema)
        query = ' query { connections { id } }'
        query_result = client.execute(query)
        num_ids = len(query_result['data']['connections'])
        next_conn_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['connections'])
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
        next_id = check_num_ids(num_ids=num_ids, result_dict=query_result['data']['sqlQueries'])
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

        query = ' query { sqlQuery (request: "' + request + '") { id request connectionsId } }'
        query_result = client.execute(query)
        self.assertEqual(request, query_result['data']['sqlQuery']['request'])  # Assert query read successful

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
