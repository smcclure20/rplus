#!/bin/bash

import sys

f = open(sys.argv[1], "r")

scores = []
for line in f.readlines():
    if line.startswith("score: "):
        score = float(line.split(" ")[1].strip())
        if score > 0:
            scores.append(score)


print("Score: ", sum(scores)/len(scores))
print("Number of non-zero scores: ", len(scores))

