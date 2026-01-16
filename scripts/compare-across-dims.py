#!/bin/bash

# Gets the actions for a midpoint in each whisker of the first whisker tree provided, ignoring some dimensions
# Therefore, for every whisker in the first whisker tree, there will be a whisker in the output 

import sys

from protobufs.dna_pb2 import WhiskerTree, Memory

def load_whiskers(whisker_file_name):
    # Read the whiskers in 
    fd = open(whisker_file_name, "rb")
    tree = fd.read()
    whiskertree = WhiskerTree()
    whiskertree.ParseFromString(tree)
    return whiskertree


def mem_str(memory):
    return "<sewma={}, recwma={}, rttr={}, slow_recwma={}, loss={}, intq={}, intl={}>".format(memory.rec_send_ewma, memory.rec_rec_ewma, memory.rtt_ratio, memory.slow_rec_rec_ewma, memory.recent_loss, memory.int_queue, memory.int_link)

def mem_range_str(memory_range):
    return "(low: {}, hi: {}".format(mem_str(memory_range.lower), mem_str(memory_range.upper))

def whisker_str(whisker):
    return "[{} => ({} + {} * win, pace={})]".format(mem_range_str(whisker.domain), whisker.window_increment, whisker.window_multiple, whisker.intersend)

def whisker_matches(whisker, point, ignored_dim=None): # TODO: CHECK BOUNDS
    if not (whisker.domain.lower.rec_send_ewma <= point.rec_send_ewma and whisker.domain.upper.rec_send_ewma > point.rec_send_ewma):
        return False
    if not (whisker.domain.lower.rec_rec_ewma <= point.rec_rec_ewma and whisker.domain.upper.rec_rec_ewma > point.rec_rec_ewma):
        return False
    if not (whisker.domain.lower.rtt_ratio <= point.rtt_ratio and whisker.domain.upper.rtt_ratio > point.rtt_ratio):
        return False
    if not (whisker.domain.lower.slow_rec_rec_ewma <= point.slow_rec_rec_ewma and whisker.domain.upper.slow_rec_rec_ewma > point.slow_rec_rec_ewma):
        return False
    if not (whisker.domain.lower.recent_loss <= point.recent_loss and whisker.domain.upper.recent_loss > point.recent_loss):
        return False
    if ignored_dim != "int_queue" and not (whisker.domain.lower.int_queue <= point.int_queue and whisker.domain.upper.int_queue > point.int_queue):
        return False
    if ignored_dim != "int_link" and not (whisker.domain.lower.int_link <= point.int_link and whisker.domain.upper.int_link > point.int_link):
        return False
    return True

def find_matching_whisker(whiskertree, point, ignored_dim=None):
    if len(whiskertree.children) == 0:
        if whisker_matches(whiskertree.leaf, point, ignored_dim):
            return whiskertree.leaf
        else:
            return None
    
    else:
        for child in whiskertree.children:
            matching_whisker = find_matching_whisker(child, point, ignored_dim)
            if matching_whisker != None:
                return matching_whisker
            
    return None


def get_all_whiskers(whiskertree):
    all_whiskers = []
    if len(whiskertree.children) == 0:
        return [whiskertree.leaf]
    
    else:
        for child in whiskertree.children:
            all_whiskers += get_all_whiskers(child)
    
    return all_whiskers

def get_dim_midpoint(lower, upper):
    return (upper + lower) / 2

def get_midpoint(whisker):
    point = Memory()
    memory_range = whisker.domain
    point.rec_send_ewma = get_dim_midpoint(memory_range.lower.rec_send_ewma, memory_range.upper.rec_send_ewma)
    point.rec_rec_ewma = get_dim_midpoint(memory_range.lower.rec_rec_ewma, memory_range.upper.rec_rec_ewma)
    point.rtt_ratio = get_dim_midpoint(memory_range.lower.rtt_ratio, memory_range.upper.rtt_ratio)
    point.slow_rec_rec_ewma = get_dim_midpoint(memory_range.lower.slow_rec_rec_ewma, memory_range.upper.slow_rec_rec_ewma)
    point.recent_loss = get_dim_midpoint(memory_range.lower.recent_loss, memory_range.upper.recent_loss)
    point.int_queue = get_dim_midpoint(memory_range.lower.int_queue, memory_range.upper.int_queue)
    point.int_link = get_dim_midpoint(memory_range.lower.int_link, memory_range.upper.int_link)
    return point


def match_whiskers(more_signal_tree, fewer_signal_tree, ignored_dim, output_file):
    fd = open(output_file, "w")
    fd.write("sewma,rewma,rttr,srewma,loss,queue,link,incr1,mult1,inter1,incr2,mult2,inter2\n")
    more_signals_tree_whiskers = get_all_whiskers(more_signal_tree)
    for whisker in more_signals_tree_whiskers:
        midpoint = get_midpoint(whisker)
        matching_whisker = find_matching_whisker(fewer_signal_tree, midpoint, ignored_dim=ignored_dim)
        if matching_whisker == None:
            print("ERROR: NO MATCHING WHISKERS")
            print(whisker_str(whisker))
            print(mem_str(midpoint))
        
        fd.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(midpoint.rec_send_ewma, midpoint.rec_rec_ewma, 
                                                                   midpoint.rtt_ratio, midpoint.slow_rec_rec_ewma, 
                                                                   midpoint.recent_loss, midpoint.int_queue, 
                                                                   midpoint.int_link, whisker.window_increment,
                                                                   whisker.window_multiple, whisker.intersend, 
                                                                   matching_whisker.window_increment, matching_whisker.window_multiple, 
                                                                   matching_whisker.intersend))
        # print(mem_str(midpoint))
        # print("{}, {}, {}".format(diff[0], diff[1], diff[2]))

    fd.close()


if __name__ == "__main__":
    reference_whisker_file = sys.argv[1]
    whisker_file = sys.argv[2]
    output_file = sys.argv[3]
    ref_whiskertree = load_whiskers(reference_whisker_file)
    whiskertree = load_whiskers(whisker_file)
    # print_tree(whiskertree)
    whiskers = match_whiskers(ref_whiskertree, whiskertree, "int_queue", output_file)
    
