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

def whisker_int_queue_adj_constraint(whisker1, whisker2):
    return whisker1.domain.upper.int_queue == whisker2.domain.lower.int_queue or whisker1.domain.lower.int_queue == whisker2.domain.upper.int_queue

def whisker_int_link_adj_constraint(whisker1, whisker2):
    return whisker1.domain.upper.int_link == whisker2.domain.lower.int_link or whisker1.domain.lower.int_link == whisker2.domain.upper.int_link

    
def get_queue_win_inc_score(whisker1, whisker2, per_step=False): #whisker.window_increment, whisker.window_multiple, whisker.intersend
    if per_step:
        return abs(whisker1.window_increment - whisker2.window_increment )
    return abs(whisker1.window_increment - whisker2.window_increment ) / abs(whisker1.domain.lower.int_queue - whisker2.domain.lower.int_queue)

def get_queue_win_mult_score(whisker1, whisker2, per_step=False):
    if per_step:
        return abs(whisker1.window_multiple - whisker2.window_multiple )
    return abs(whisker1.window_multiple - whisker2.window_multiple ) / abs(whisker1.domain.lower.int_queue - whisker2.domain.lower.int_queue)

def get_queue_intersend_score(whisker1, whisker2, per_step=False):
    if per_step:
        return abs(whisker1.intersend - whisker2.intersend )
    return abs(whisker1.intersend - whisker2.intersend ) / abs(whisker1.domain.lower.int_queue - whisker2.domain.lower.int_queue)

def get_link_win_inc_score(whisker1, whisker2, per_step=False): 
    if per_step:
        return abs(whisker1.window_increment - whisker2.window_increment )
    return abs(whisker1.window_increment - whisker2.window_increment ) / abs(whisker1.domain.lower.int_link - whisker2.domain.lower.int_link)

def get_link_win_mult_score(whisker1, whisker2, per_step=False): 
    if per_step:
        return abs(whisker1.window_multiple - whisker2.window_multiple )
    return abs(whisker1.window_multiple - whisker2.window_multiple ) / abs(whisker1.domain.lower.int_link - whisker2.domain.lower.int_link)

def get_link_intersend_score(whisker1, whisker2, per_step=False): 
    if per_step:
        return abs(whisker1.intersend - whisker2.intersend )
    return abs(whisker1.intersend - whisker2.intersend ) / abs(whisker1.domain.lower.int_link - whisker2.domain.lower.int_link)


def get_importance_score_for_whisker(whiskertree, adjacency_constraint, reference_whisker, scoring_function):
    score = 0
    if len(whiskertree.children) == 0:
        if adjacency_constraint(reference_whisker, whiskertree.leaf):
            return scoring_function(reference_whisker, whiskertree.leaf, per_step=True)
        else:
            return 0
    
    else:
        for child in whiskertree.children:
            score += get_importance_score_for_whisker(child, adjacency_constraint, reference_whisker, scoring_function)
    
    return score

def get_whiskers(whiskertree):
    all_whiskers = []
    if len(whiskertree.children) == 0:
        return [whiskertree.leaf]
    
    else:
        for child in whiskertree.children:
            all_whiskers += get_whiskers(child)
    
    return all_whiskers

def get_int_importance(whiskertree, adjaceny_constraint, scoring_function):
    all_whiskers = get_whiskers(whiskertree)
    total_score = 0
    for whisker in all_whiskers:
        total_score += get_importance_score_for_whisker(whiskertree, adjaceny_constraint, whisker, scoring_function)
    return total_score


if __name__ == "__main__":
    whisker_file = sys.argv[1]
    whiskertree = load_whiskers(whisker_file)
    queue_win_inc_score = get_int_importance(whiskertree, whisker_int_queue_adj_constraint, get_queue_win_inc_score)
    queue_win_mult_score = get_int_importance(whiskertree, whisker_int_queue_adj_constraint, get_queue_win_mult_score)
    queue_intersend_score = get_int_importance(whiskertree, whisker_int_queue_adj_constraint, get_queue_intersend_score)
    print("Queue Stats:")
    print("Window Increment Score: {}".format(queue_win_inc_score))
    print("Window Multiple Score: {}".format(queue_win_mult_score))
    print("Intersend Score: {}".format(queue_intersend_score))

    link_win_inc_score = get_int_importance(whiskertree, whisker_int_link_adj_constraint, get_link_win_inc_score)
    link_win_mult_score = get_int_importance(whiskertree, whisker_int_link_adj_constraint, get_link_win_mult_score)
    link_intersend_score = get_int_importance(whiskertree, whisker_int_link_adj_constraint, get_link_intersend_score)
    print("Link Stats:")
    print("Window Increment Score: {}".format(link_win_inc_score))
    print("Window Multiple Score: {}".format(link_win_mult_score))
    print("Intersend Score: {}".format(link_intersend_score))
