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

    def get_current_chain_name(self) -> str:
        return self.chain[self.current_chain].chain_name

    def create_table(self, table: str) -> str:
        self.table = table
        command = f"create table inet {table}"
        return self.cmd(command)

    def add_chain(self, chain: str) -> str:
        self.current_chain = chain
        self.chain.update({chain: Chain(chain)})
        command = f"add chain inet {self.table} {self.get_current_chain_name()} {{ type filter hook output priority 0; }}"
        return self.cmd(command)

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

    def _build_rule(self, rule_type: str, values) -> str:
        rule = "add rule "

        rule += values["family"] if "family" in values else "inet"

        rule += f" {self.table} {self.get_current_chain_name()}"
        if "saddr" in values:
            rule += f" ip saddr {values['saddr']}"
        if "daddr" in values:
            rule += f" ip daddr {values['daddr']}"
        if "sport" in values:
            rule += f" tcp sport {values['sport']}"
        if "dport" in values:
            rule += f" tcp dport {values['dport']}"

        rule += f" {rule_type}"

        return rule

    def accept(self, **values) -> str:
        """Accept the list of values provided.

        Returns:
            str: Output of the nft cmd
        """
        rule = self._build_rule("accept", values)
        return self.cmd(rule)

    def drop(self, **values):
        """Drops the list of values provided.

        Returns:
            str: Output of the nft cmd
        """
        rule = self._build_rule("drop", values)
        return self.cmd(rule)

    def get_resource(self):
        return self.nft

    def delete_chain(self, chain: str) -> str:
        """Delete the chain given.

        Args:
            chain (str, optional): Defaults to None.
        """
        if chain not in self.chain:
            raise Exception(f"No chain {chain} found")

        chain_name = self.chain[chain].chain_name
        del self.chain[chain]
        return self.cmd(f"delete chain inet {self.table} {chain_name}")


class Chain:
    def __init__(self, chain: str) -> None:
        '''nftable doesn't allow strings to start with numeric values'''
        self.chain_id = chain
        self.chain_name = re.sub(r'[0-9]+', '', chain)

