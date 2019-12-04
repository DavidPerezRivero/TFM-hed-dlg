"""
Takes as input a triple file and creates a processed version of it.
If given an external dictionary, the input triple file will be converted
using that input dictionary.

@author Alessandro Sordoni, Iulian Vlad Serban
"""

import collections
import numpy
import operator
import os
import sys
import logging
import pickle as cPickle
import itertools
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('text2dict')

def safe_pickle(obj, filename):
    if os.path.isfile(filename):
        logger.info("Overwriting %s." % filename)
    else:
        logger.info("Saving to %s." % filename)

    with open(filename, 'wb') as f:
        cPickle.dump(obj, f, protocol=cPickle.HIGHEST_PROTOCOL)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Tab separated dialogue file (assumed shuffled)")
parser.add_argument("--cutoff", type=int, default=-1, help="Vocabulary cutoff (optional)")
parser.add_argument("--dict", type=str, default="", help="External dictionary (pkl file)")
parser.add_argument("--use_all_dialogues", action='store_true', help="If false, only examples with exactly three tripels will be used and all others discarded. If true, all examples will be used.")
parser.add_argument("--force_triple_format", action='store_true', help="Requires use_all_dialogues set to true. If true, training examples with less than three utterances will have empty utterances appended at the beginning, and training examples with more than three utterances will have their first utterances discarded.")

parser.add_argument("output", type=str, help="Prefix of the pickle binarized triple corpus")
args = parser.parse_args()

if not os.path.isfile(args.input):
    raise Exception("Input file not found!")

if args.force_triple_format==True and args.use_all_dialogues==False:
    raise Exception("Inconsistent flags. To force all dialogues into triple format, first set the flag use_all_dialogues.")

unk = "<unk>"

###############################
# Part I: Create the dictionary
###############################
if args.dict != "":
    # Load external dictionary
    assert os.path.isfile(args.dict)
    vocab = dict([(x[0], x[1]) for x in cPickle.load(open(args.dict, "r"))])

    # Check consistency
    assert '<unk>' in vocab
    assert '<s>' in vocab
    assert '</s>' in vocab
else:
    word_counter = Counter()


    for line in open(args.input, 'r'):
        s = [x for x in line.strip().split()]
        word_counter.update(s)

    total_freq = sum(word_counter.values())
    logger.info("Total word frequency in dictionary %d " % total_freq)

    if args.cutoff != -1:
        logger.info("Cutoff %d" % args.cutoff)
        vocab_count = word_counter.most_common(args.cutoff)
    else:
        vocab_count = word_counter.most_common()


    # Add special tokens to the vocabulary
    vocab = {'<unk>': 0, '<s>': 1, '</s>': 2}
    for i, (word, count) in enumerate(vocab_count):
        vocab[word] = i + 3


logger.info("Vocab size %d" % len(vocab))

#################################
# Part II: Binarize the triples
#################################

# Everything is loaded into memory for the moment
binarized_corpus = []
# Some statistics
mean_sl = 0.
unknowns = 0.
num_terms = 0.
freqs = collections.defaultdict(lambda: 0)

# counts the number of triples each unique word exists in; also known as document frequency
df = collections.defaultdict(lambda: 0)

for line, triple in enumerate(open(args.input, 'r')):
    triple_lst = []

    utterances = triple.split('\t')
    for i, utterance in enumerate(utterances):

        utterance_lst = []
        for word in utterance.strip().split():
            word_id = vocab.get(word, 0)
            unknowns += 1 * (word_id == 0)
            utterance_lst.append(word_id)
            freqs[word_id] += 1

        num_terms += len(utterance_lst)

        # Here, we filter out unknown triple text and empty triples
        # i.e. <s> </s> or <s> 0 </s>
        if utterance_lst != [0] and len(utterance_lst):
            triple_lst.append([1] + utterance_lst + [2])
            freqs[1] += 1
            freqs[2] += 1
            df[1] += 1
            df[2] += 1

    if args.force_triple_format == True:
        if len(triple_lst) > 3:
            triple_lst = triple_lst[len(triple_lst)-2:len(triple_lst)]
        else:
            while len(triple_lst) < 3:
                triple_lst.insert(0, [1] + [2])


    if (args.use_all_dialogues ==True) or (len(triple_lst) == 3):
        # Flatten out binarized triple
        # [[a, b, c], [c, d, e]] -> [a, b, c, d, e]
        binarized_triple = list(itertools.chain(*triple_lst))
        binarized_corpus.append(binarized_triple)

    unique_word_indices = []
    for i in range(len(triple_lst)):
        for word_id in triple_lst[i]:
            unique_word_indices.append(word_id)

    unique_word_indices = set(unique_word_indices)
    for word_id in unique_word_indices:
        df[word_id] += 1

safe_pickle(binarized_corpus, args.output + ".triples.pkl")

if args.dict == "":
     safe_pickle([(word, word_id, freqs[word_id], df[word_id]) for word, word_id in vocab.items()], args.output + ".dict.pkl")

logger.info("Number of unknowns %d" % unknowns)
logger.info("Number of terms %d" % num_terms)
logger.info("Mean triple length %f" % float(sum(map(len, binarized_corpus))/len(binarized_corpus)))
logger.info("Writing training %d triples (%d left out)" % (len(binarized_corpus), line + 1 - len(binarized_corpus)))
