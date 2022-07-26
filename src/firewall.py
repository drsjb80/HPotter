import nftables
import json
import re


class Firewall:
    """A simple nft manager for firewall rules

    References: https://github.com/aborrero/python-nftables-tutorial
    """

    def __init__(self) -> None:
        # Consider loading in the list of rules json and then add hpotter table to manage
        self.nft = nftables.Nftables()
        self.nft.set_json_output(True)
        self.table = None
        self.chain = {}
        self.current_chain = None

    def set_table(self, table: str) -> None:
        self.table = table

    def set_chain(self, chain: str) -> None:
        self.current_chain = chain

    def get_current_chain(self):
        return self.chain[self.current_chain]

    def get_current_chain_name_input(self) -> str:
        return self.chain[self.current_chain][Chain.INPUT].chain_name

    def get_current_chain_name_output(self) -> str:
        return self.chain[self.current_chain][Chain.OUTPUT].chain_name

    def create_table(self, table: str) -> str:
        self.table = table
        command = f"create table inet {table}"
        return self.cmd(command)

    def add_chain(self, chain: str) -> list:
        self.current_chain = chain
        outputs = []
        ObjChain = Chain(chain)

        update_chain = {chain: {Chain.INPUT: ObjChain}}
        update_chain[chain].update({Chain.OUTPUT: ObjChain})
        self.chain.update(update_chain)

        command = f"add chain inet {self.table} input_{self.get_current_chain_name_input()} {{ type filter hook input priority 0; }}"
        outputs += self.cmd(command)

        command = f"add chain inet {self.table} output_{self.get_current_chain_name_output()} {{ type filter hook output priority 0; }}"
        outputs += self.cmd(command)

        return outputs

    def cmd(self, command: str) -> str:
        """Run a nft command

        Args:
            command (str): Requires a valid nft command

        Raises:
            Exception: Will provide information on what went wrong.

        Returns:
            str: The nft command output
        """
        rc, output, error = self.nft.cmd(command)
        if error or rc != 0:
            raise Exception(
                f"cmd: {error} while running {command}"
                if error
                else f"cmd: There was an error " f"while running: {command}"
            )
        return output

    def flush(self):
        self.nft.cmd("flush ruleset")

    def list_rules(self, print_the_rules: bool = False):
        if print_the_rules:
            print(json.loads(self.cmd("list ruleset")))
        else:
            return json.loads(self.cmd("list ruleset"))

    def _build_rule(self, rule_type: str, values, inbound: bool = True) -> str:
        rule = "add rule "

        rule += values["family"] if "family" in values else "inet"

        if inbound:
            rule += f" {self.table} {Chain.INPUT}_{self.get_current_chain_name_input()} log"
            if "saddr" in values:
                rule += f" ip saddr {values['saddr']}"
            if "daddr" in values:
                rule += f" ip daddr {values['daddr']}"
            if "sport" in values:
                rule += f" tcp sport {values['sport']}"
            if "dport" in values:
                rule += f" tcp dport {values['dport']}"
        else:
            rule += f" {self.table} {Chain.OUTPUT}_{self.get_current_chain_name_output()} log"
            if "daddr" in values:
                rule += f" ip daddr {values['daddr']}"
            if "saddr" in values:
                rule += f" ip saddr {values['saddr']}"
            if "dport" in values:
                rule += f" tcp dport {values['dport']}"
            if "sport" in values:
                rule += f" tcp sport {values['sport']}"
        rule += f" {rule_type}"

        return rule

    def add_rule(self, rule_type: str, **values) -> list:
        """Accept the list of values provided.

        Returns:
            str: Output of the nft cmd
        """
        outputs = []
        rule = self._build_rule(rule_type, values, True)
        outputs += self.cmd(rule)
        rule = self._build_rule(rule_type, values, False)
        outputs += self.cmd(rule)

        return outputs

    def get_resource(self):
        return self.nft

    def delete_chain(self, chain: str) -> str:
        """Delete the chain given.

        Args:
            chain (str, optional): Defaults to None.
        """
        if chain not in self.chain:
            raise Exception(f"No chain {chain} found")

        self.current_chain = chain
        chain_name_input = self.get_current_chain_name_input()
        chain_name_output = self.get_current_chain_name_output()
        del self.chain[chain]
        outputs = []
        outputs += self.cmd(f"delete chain inet {self.table} {Chain.INPUT}_{chain_name_input}")
        outputs += self.cmd(f"delete chain inet {self.table} {Chain.OUTPUT}_{chain_name_output}")

        return outputs


class Chain:
    INPUT = "input"
    OUTPUT = "output"

    def __init__(self, chain: str, inbound: bool = True) -> None:
        '''nftable doesn't allow strings to start with numeric values'''
        self.chain_id = chain
        self.chain_name = re.sub(r'[0-9]+', '', chain)
        self.inbound = inbound
        self.outbound = not inbound  # might not need this
