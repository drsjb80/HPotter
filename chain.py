import iptc

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

def delete_drop_rules():
    for rule, chain in zip(hpotter_chain_rules, builtin_chains):
        chain.delete_rule(rule)

    for chain in hpotter_chains:
        chain.delete_rule(drop_rule)

    for chain in hpotter_chains:
        chain.delete()


add_drop_rules()
delete_drop_rules()
