#!/usr/bin/python

"Assignment 4 - This is the controller code that students will have to \
    implement sections of. It is Pyretic based, but this is somewhat\
    unimportant at the moment, as we only care about the learning\
    behaviors."

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import packets
from helpers import *


class LearningSwitch(DynamicPolicy):
    def __init__(self):
        """ Initialization of the Learning Switch. The important piece
            is the definition of the switch mapping. This is a nested
            dictionary. """

        # Initialize the parent class
        super(LearningSwitch, self).__init__()

        # TODO: Initialize your forwarding tables. Create this however you wish.
        # Couple of suggestions: Dictionary of dictionaries, Dictionary of 
        # tuples. 

        self.forward_table = {}
        self.forward_table['1'] = {}
        self.forward_table['2'] = {}
        self.forward_table['3'] = {}
        self.forward_table['4'] = {}
        self.forward_table['5'] = {}

        # only use one flood instance - this is the default policy when there 
        # isn't a known path.
        self.flood = flood()

        # Get the first packet from each new MAC address on a switch. This
        # is how we are able to learn new routes.
        new_pkts = packets(1, ['srcmac', 'switch'])
        new_pkts.register_callback(self.learn_route)
        self.query = new_pkts

        # Initialize the policy
        self.build_policy() 


    def print_switch_tables(self):
        # TODO - You will need to implement this based on how your forwarding
        # table are set up. Us the functions in the first half of helpers.
        # Format should be to call write_forwarding_entry() for each entry in
        # the forwarding table, then finish up with finish_printing(). 
        open_log("learning-switch.log")
        for entry in self.forward_table.keys():
            for rule in self.forward_table[entry].keys():
                write_forwarding_entry(int(entry), int(self.forward_table[entry][rule]), rule)
        next_entry()
        finish_log()
        pass

    def learn_route(self, pkt):
        """  This function adds new routes into the fowarding table. """

        # TODO - create a new entry in the fowarding table. Use the functions 
        # in the second half of helpers to simplify all your work.    

        self.forward_table[str(get_switch(pkt))][str(get_src_mac(pkt))] = get_inport(pkt)

        # print out the switch tables:
        self.print_switch_tables()

        # Call build_policy to update the fowarding tables of the switches.
        self.build_policy()
        pass




    def build_policy(self):
        """ 
        This is similar to the build_policy() function in StaticSwitch. 
        There is a major difference: If there isn't a rule, you need to flood
        the packets. The example code should help.
        """
        new_policy = None
        not_flood_pkts = None
        

        # TODO: Example code. You will need to edit this based on how you're 
        # storing your policies. You should only have to replace the details in
        # rule entries.
        for entry in self.forward_table.keys():
            for rule in self.forward_table[entry].keys():
                if new_policy == None:
                    new_policy = (match(switch=int(entry), dstmac=rule) >> 
                                  fwd(self.forward_table[entry][rule]))
                else:
                    new_policy += (match(switch=int(entry), dstmac=rule) >> 
                                   fwd(self.forward_table[entry][rule]))
                
                if not_flood_pkts == None:
                    not_flood_pkts = (match(switch=int(entry), dstmac=rule))
                else:
                    not_flood_pkts |= (match(switch=int(entry), dstmac=rule))
                        
                

        # If you follow the pattern above, you won't have to change this below. 
        # We don't know of any rules yet, so flood everything.
        if not_flood_pkts == None:
            self.policy = self.flood + self.query
        else:
            self.policy = if_(not_flood_pkts, new_policy, self.flood) + self.query
        
        # The following line can be uncommented to see your policy being
        # built up, say during a flood period. 
        # print self.policy


def main():
    return LearningSwitch()

