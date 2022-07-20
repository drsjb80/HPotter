import nftables
import json
from string import digits



class Firewall:
    def __init__(self) -> None:
        # Consider loading in the list of rules json and then add hpotter table to manage
        self.nft = nftables.Nftables()
        self.nft.set_json_output(True)
        self.table = None
        self.chain = None

    def set_table(self, table: str) -> None:
        self.table = table

    def set_chain(self, chain: str) -> None:
        self.chain = chain
        # chain.translate(None, digits)

    def create_table(self, table: str) -> None:
        self.cmd(f"create table inet {table}")
        # TODO Validate that it worked
        self.table = table

    def add_chain(self, chain: str) -> None:
        self.cmd(f"add chain inet {self.table} {chain}")
        # TODO Validate that it worked
        self.chain = chain

    def add_chain_to_table(self, chain: str, table: str):
        self.nft.cmd(f"add chain inet {table} {chain}")

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
            # raise Exception(
            return (
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

        rule += values['family'] if 'family' in values else 'inet'

        rule += f" {self.table} {self.chain}"
        if 'saddr' in values:
            rule += f" ip saddr {values['saddr']}"
        if 'daddr' in values:
            rule += f" ip daddr {values['daddr']}"
        if 'sport' in values:
            rule += f" tcp sport {values['sport']}"
        if 'dport' in values:
            rule += f" tcp dport {values['dport']}"

        rule += f" {rule_type}"

        return rule

    def accept(self, **values) -> str:
        """Accept the list of values provided.

        Returns:
            str: Output of the nft cmd
        """
        rule = self._build_rule('accept', values)
        return self.cmd(rule)

    def drop(self, **values):
        """Drops the list of values provided.

        Returns:
            str: Output of the nft cmd
        """
        rule = self._build_rule('drop', values)
        return self.cmd(rule)

    def block_all(self, chain: str = None):
        rule = f"type filter hook {chain if chain else self.chain} priority 0; policy drop;"
        return self.cmd(rule)

    def get_resource(self):
        return self.nft

    def delete_chain(self, chain: str = None):
        """Delete the chain given.

        Args:
            chain (str, optional): Defaults to None.
        """

        self.cmd("flush rule filter %s".format(chain if chain else self.chain))
