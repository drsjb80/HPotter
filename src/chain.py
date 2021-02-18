import iptc
import time

from src.logger import logger

# here's the idea. create hpotter chains that mirror the three bultins. add
# drop rules at the end of the hpotter chains. insert a target of each of
# the hpotter chains at the beginning of the builtin chains. this
# overwrites whatever was there. make the process reversable so that we can
# put it back the way it was.

# can only set policies in builtin chains

filter_table = iptc.Table(iptc.Table.FILTER)

input_chain = iptc.Chain(filter_table, 'INPUT')
output_chain = iptc.Chain(filter_table, 'OUTPUT')
forward_chain = iptc.Chain(filter_table, 'FORWARD')
builtin_chains = [input_chain, output_chain, forward_chain]

hpotter_input_chain = filter_table.create_chain("hpotter_input")
hpotter_output_chain = filter_table.create_chain("hpotter_output")
hpotter_forward_chain = filter_table.create_chain("hpotter_forward")
hpotter_chains = [hpotter_input_chain, hpotter_output_chain, hpotter_forward_chain]

hpotter_input_chain_rule = iptc.Rule()
hpotter_output_chain_rule = iptc.Rule()
hpotter_forward_chain_rule = iptc.Rule()
hpotter_chain_rules = [hpotter_input_chain_rule, hpotter_output_chain_rule, hpotter_forward_chain_rule]

drop_rule = iptc.Rule()
drop_rule.target = iptc.Target(drop_rule, "DROP")

cout_rule = { \
        'target': 'ACCEPT', \
        'match': 'state', \
        'state': 'NEW,ESTABLISHED,RELATED'
}

cin_rule = { \
        'target': 'ACCEPT', \
        'match': 'state', \
        'state': 'ESTABLISHED,RELATED'
}


def add_drop_rules():
    # append drop to all hpotter chains
    for chain in hpotter_chains:
        chain.append_rule(drop_rule)

    # create target for all hpotter chains
    for rule, chain in zip(hpotter_chain_rules, hpotter_chains):
        rule.target = iptc.Target(rule, chain.name)

    # make the hpotter chains the target for all builtin chains
    for rule, chain in zip(hpotter_chain_rules, builtin_chains):
        chain.insert_rule(rule)

    iptc.easy.insert_rule('filter', 'OUTPUT', cout_rule)
    iptc.easy.insert_rule('filter', 'INPUT', cin_rule)

def delete_drop_rules():
    for rule, chain in zip(hpotter_chain_rules, builtin_chains):
        chain.delete_rule(rule)

    for chain in hpotter_chains:
        # chain.delete_rule(drop_rule)
        chain.flush()

    for chain in hpotter_chains:
        chain.delete()

    iptc.easy.delete_rule('filter', "OUTPUT", cout_rule)
    iptc.easy.delete_rule('filter', "INPUT", cin_rule)

def create_rules(obj): #TODO: refactor (possibly use a dispatcher)
    if type(obj).__name__ == 'ContainerThread':
        proto = obj.container_protocol.lower()
        source_addr = "172.17.0.1"
        dest_addr = obj.container_ip
        dstport = str(obj.container_port)
    
        obj.to_rule = { \
                'src': source_addr, \
                'dst': dest_addr, \
                'target': 'ACCEPT', \
                'protocol': proto, \
                proto: {'dport': dstport} \
        }
        logger.debug(obj.to_rule)
        iptc.easy.insert_rule('filter', 'hpotter_output', obj.to_rule)

        obj.from_rule = { \
                'src': dest_addr, \
                'dst': source_addr, \
                'target': 'ACCEPT', \
                'protocol': proto, \
                proto: {'sport': dstport} \
        }
        logger.debug(obj.from_rule)
        iptc.easy.insert_rule('filter', 'hpotter_input', obj.from_rule)

        obj.drop_rule = { \
            'src': dest_addr, \
            'dst': '!' + source_addr + "/16", \
            'target': 'DROP' \
        }
        logger.debug(obj.drop_rule)
        iptc.easy.insert_rule('filter', 'hpotter_input', obj.drop_rule)

    elif type(obj).__name__ == 'ListenThread':
        proto = "tcp"

        obj.to_rule = { \
            'target': 'ACCEPT', \
            'protocol': proto, \
            proto: {'dport': str(obj.listen_port)} \
        }
        logger.debug(obj.to_rule)
        iptc.easy.insert_rule('filter', 'hpotter_input', obj.to_rule)

        obj.from_rule = { \
            'target': 'ACCEPT', \
            'protocol': proto, \
            proto: {'sport': str(obj.listen_port)} \
        }
        logger.debug(obj.from_rule)
        iptc.easy.insert_rule('filter', 'hpotter_output', obj.from_rule)


def remove_rules(obj): #TODO: refactor (turn off autocommit and delete multiple rules at once?)
    logger.debug('Removing rules')
    if type(obj).__name__ == 'ContainerThread':
        iptc.easy.delete_rule('filter', "hpotter_output", obj.to_rule)
        iptc.easy.delete_rule('filter', "hpotter_input", obj.from_rule)
        iptc.easy.delete_rule('filter', "hpotter_input", obj.drop_rule)
    elif type(obj).__name__ == 'ListenThread':
        iptc.easy.delete_rule('filter', "hpotter_input", obj.to_rule)
        iptc.easy.delete_rule('filter', "hpotter_output", obj.from_rule)