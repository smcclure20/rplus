#!/bin/bash

# Gets the whisker actions for a midpoint in each whisker of the first whisker tree provided
# I am pretty sure these scripts do the exact same thing

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

def whisker_matches(whisker, point): # TODO: CHECK BOUNDS
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
    if not (whisker.domain.lower.int_queue <= point.int_queue and whisker.domain.upper.int_queue > point.int_queue):
        return False
    if not (whisker.domain.lower.int_link <= point.int_link and whisker.domain.upper.int_link > point.int_link):
        return False
    return True

#<sewma=1.4973860841911695, recwma=1.4994381909303827, rttr=0.5336799416260534, slow_recwma=1.3075192707138257, loss=81920.0, intq=4.90594251690649, intl=0.22062364684167482>

def find_matching_whisker(whiskertree, point):
    if len(whiskertree.children) == 0:
        if whisker_matches(whiskertree.leaf, point):
            return whiskertree.leaf
        else:
            return None
    
    else:
        for child in whiskertree.children:
            found = find_matching_whisker(child, point)
            if found != None:
                return found
    

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

def diff_whiskers(whisker1, whisker2):
    window_inc_diff = whisker1.window_increment - whisker2.window_increment
    window_mult_diff = whisker1.window_multiple - whisker2.window_multiple
    intersend_diff = whisker1.intersend - whisker2.intersend
    return (window_inc_diff, window_mult_diff, intersend_diff)

def match_whiskers(reference_tree, tree, output_file):
    fd = open(output_file, "w")
    fd.write("sewma,rewma,rttr,srewma,loss,queue,link,incr1,mult1,inter1,incr2,mult2,inter2\n")
    reference_tree_whiskers = get_all_whiskers(reference_tree)
    for whisker in reference_tree_whiskers:
        midpoint = get_midpoint(whisker)
        found_whisker = find_matching_whisker(tree, midpoint)
        if found_whisker == None:
            print("ERROR: NO MATCHING WHISKER")
            print(whisker_str(whisker))
            print(mem_str(midpoint))
        # diff = diff_whiskers(whisker, found_whisker)
        
        fd.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(midpoint.rec_send_ewma, midpoint.rec_rec_ewma, 
                                                                   midpoint.rtt_ratio, midpoint.slow_rec_rec_ewma, 
                                                                   midpoint.recent_loss, midpoint.int_queue, 
                                                                   midpoint.int_link, whisker.window_increment,
                                                                   whisker.window_multiple, whisker.intersend,
                                                                   found_whisker.window_increment, found_whisker.window_multiple, 
                                                                   found_whisker.intersend))
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
    whiskers = match_whiskers(ref_whiskertree, whiskertree, output_file)
    
