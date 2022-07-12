import nftables
import json

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
            raise Exception(
                f"cmd: {error} while running {command}"
                if error
                else f"cmd: There was an error " f"while running: {command}"
            )
        return output

    def flush(self):
        self.nft.cmd('flush ruleset')

    def list_rules(self):
        print(json.loads(self.cmd('list ruleset')))

    def accept(self, **values) -> str:
        """Accept the list of values provided.

        TODO Add in conditions for variations of whether or not the valeus exsits and added them accordingly e.g. saddr and daddr.

        Returns:
            str: Output of the nft cmd
        """
        rule=f"add rule {values['type']} {self.table} {self.chain} ip saddr {values['saddr']} ip daddr {values['daddr']} tcp sport {values['sport']} tcp dport {values['dport']} accept"
        return self.cmd(rule)

    def drop(self, **values):
        """Drops the list of values provided.

        TODO Add in conditions for variations of whether or not the valeus exsits and added them accordingly e.g. saddr and daddr.
        Returns:
            str: Output of the nft cmd
        """
        rule=f"add rule {values['type']} {self.table} {self.chain} ip saddr {values['saddr']} tcp sport {values['sport']} drop"
        return self.cmd(rule)

    def get_resource(self):
        return self.nft
