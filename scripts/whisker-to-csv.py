#!/bin/bash

import sys

from protobufs.dna_pb2 import WhiskerTree

def load_whiskers(whisker_file_name):
    # Read the whiskers in 
    fd = open(whisker_file_name, "rb")
    tree = fd.read()
    whiskertree = WhiskerTree()
    whiskertree.ParseFromString(tree)
    return whiskertree


def mem_str(memory):
    return "{},{},{},{},{},{}".format(memory.rec_send_ewma, memory.rec_rec_ewma, memory.rtt_ratio, memory.slow_rec_rec_ewma, memory.int_queue, memory.int_link)

def mem_range_str(memory_range):
    return "{},{}".format(mem_str(memory_range.lower), mem_str(memory_range.upper))

def whisker_str(whisker):
    return "{},{},{},{}".format(mem_range_str(whisker.domain), whisker.window_increment, whisker.window_multiple, whisker.intersend)

def header_str():
    return "low_sewma,low_rewma,low_rttr,low_slowrewma,low_intq,low_intl,hi_sewma,hi_rewma,hi_rttr,hi_slowrewma,hi_intq,hi_intl,win_incr,win_mult,inter"

def print_tree(whiskers, output):
    if len(whiskers.children) == 0:
        output.write(whisker_str(whiskers.leaf) + "\n")
    
    else:
        for child in whiskers.children:
            print_tree(child, output)


if __name__ == "__main__":
    whisker_file = sys.argv[1]
    whiskertree = load_whiskers(whisker_file)
    output_file_name = sys.argv[2]
    op = open("./output/{}".format(output_file_name), "w")
    op.write(header_str() + "\n")
    whiskers = print_tree(whiskertree, op)
    # total_intersend = 0
    # for whisker in whiskers:
    #     total_intersend += whisker.intersend
        # print(whisker_str(whisker))
    # print(total_intersend / len(whiskers))

    # print(whiskertree.domain.active_axis)

    # count = count_whiskers_for_constraint(whiskertree, whisker_intersend_constraint)
    # print(count)
    
