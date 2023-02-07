import unittest
from unittest.mock import call, patch
import json
import uuid

from src.firewall import Firewall


class TestFirewall(unittest.TestCase):
    def setUp(self):
        self.fw = Firewall()
        self.TABLE_INDEX = 1
        self.CHAIN_INDEX = 2
        self.RULE_INDEX = 3

    def tearDown(self):
        self.fw.flush()

    def test_create_table(self):
        self.fw.nft.set_json_output(True)
        TABLE_NAME = 'hpotter'

        self.assertEqual(self.fw.create_table(TABLE_NAME), '')
        self.assertEqual(self.fw.table, TABLE_NAME)

        data = json.loads(json.dumps(self.fw.list_rules()))
        self.assertEqual(data['nftables'][self.TABLE_INDEX]['table']['name'], TABLE_NAME)

    def test_add_chain(self):
        self.fw.nft.set_json_output(True)
        TABLE_NAME = 'hpotter'
        CHAIN_NAME = str(uuid.uuid4().hex)

        output = self.fw.create_table(TABLE_NAME)
        self.assertEqual(output, '')
        output = self.fw.add_chain(CHAIN_NAME)
        self.assertEqual(output, '')
        data = json.loads(json.dumps(self.fw.list_rules()))
        self.assertEqual(data['nftables'][self.CHAIN_INDEX]['chain']['name'], self.fw.get_current_chain_name())
        self.assertNotEqual(data['nftables'][self.CHAIN_INDEX]['chain']['name'], CHAIN_NAME)

    def test_add_rule_accept_is_assigned_to_chain(self):
        self.fw.nft.set_json_output(True)
        TABLE_NAME = 'hpotter'
        CHAIN_NAME = str(uuid.uuid4().hex)

        output = self.fw.create_table(TABLE_NAME)
        self.assertEqual(output, '')
        output = self.fw.add_chain(CHAIN_NAME)
        self.assertEqual(output, '')

        self.fw.accept(
            saddr='127.0.0.1',
            daddr='197.0.0.1',
            sport='1234',
            dport='80'
        )

        data = json.loads(json.dumps(self.fw.list_rules()))
        self.assertEqual(data['nftables'][self.RULE_INDEX]['rule']['chain'], self.fw.get_current_chain_name())

    def test_add_rule_accept_has_rules(self):
        self.fw.nft.set_json_output(True)
        TABLE_NAME = 'hpotter'
        CHAIN_NAME = str(uuid.uuid4().hex)

        output = self.fw.create_table(TABLE_NAME)
        self.assertEqual(output, '')
        output = self.fw.add_chain(CHAIN_NAME)
        self.assertEqual(output, '')

        self.fw.accept(
            saddr='127.0.0.1',
            daddr='197.0.0.1',
            sport='1234',
            dport='80'
        )

        data = json.loads(json.dumps(self.fw.list_rules()))
        self.assertGreater(len(data['nftables'][self.RULE_INDEX]['rule']['expr']), 0)

    def test_delete_chain(self):
        self.fw.nft.set_json_output(True)
        TABLE_NAME = 'hpotter'
        CHAIN_NAME = str(uuid.uuid4().hex)

        output = self.fw.create_table(TABLE_NAME)
        self.assertEqual(output, '')
        output = self.fw.add_chain(CHAIN_NAME)
        self.assertEqual(output, '')

        self.fw.accept(
            saddr='127.0.0.1',
            daddr='197.0.0.1',
            sport='1234',
            dport='80'
        )
        self.fw.delete_chain(CHAIN_NAME)
        data = json.loads(json.dumps(self.fw.list_rules()))
        self.assertRaises(IndexError, lambda: data['nftables'][self.CHAIN_INDEX]['chain'])
        self.assertRaises(KeyError, lambda: self.fw.chain[CHAIN_NAME])
