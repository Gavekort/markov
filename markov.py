#!/usr/bin/env python
import argparse
from Reader import Reader
from random import randint


class Markov(object):
    # dict-index of words in chain
    word_idx = {}

    def __init__(self):
        start = Node("<s>")
        end = Node("<\s>")
        self.word_idx[hash(start.word)] = start
        self.word_idx[hash(end.word)] = end

    def add_chain(self, sentence):
        previous = self.word_idx[hash("<s>")]
        sentence.append("<\s>") # Add termination to end
        for word in sentence:
            if hash(word) in self.word_idx:  # if word in index
                node = self.word_idx[hash(word)]
            else:
                node = Node(word)
                self.word_idx[hash(word)] = node

            previous.link_to(node)
            previous = node # Move up chain

    # eta_s: lower tolerance of observations
    def traverse(self, eta_s, minlen):
        total_links = 0
        iteration = 0
        node = self.word_idx[hash("<s>")]
        list_links = []
        if len(self.word_idx) is 0:
            print("Index empty - Build chain first")
            raise
        while node is not self.word_idx[hash("<\s>")]: # While not end
            for key in node.links: # Get all the links
                link = node.links[key]
                if link.count > int(eta_s):
                    # Skip if end and iteration is not minlen
                    if link.to is self.word_idx[hash("<\s>")] \
                            and iteration < int(minlen):
                        continue
                    else:
                        # Put links in a roulette
                        total_links = total_links + link.count
                        for i in range(0, link.count):
                            list_links.append(link)
            if iteration is not 0:
                print(node.word, "", end="")
            iteration = iteration + 1
            if total_links > 2:
                # Roll roulette with 1 position per observation
                node = list_links[randint(0, total_links - 1)].to
            else:
                break
            # Reset
            total_links = 0
            list_links = []



class Node(object):
    def __init__(self, word):
        self.word = word
        self.links = {}

    # Note that links are hashed by their to-Node
    def link_to(self, to):
        if hash(to) in self.links:  # if link already established
            link = self.links[hash(to)]
            link.count = link.count + 1  # increment link counta
        else:
            link = Link(self, to)
            self.links[hash(to)] = link

class Link(object):
    def __init__(self, fr, to):
        self.fr = fr
        self.to = to
        self.count = 1

if __name__ == '__main__':
    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', default=None, nargs='?',
                        help='Destination to training-data')
    parser.add_argument('minlen', default=0, nargs='?',
                        help='Minimum length to try')
    parser.add_argument('eta_s', default=0, nargs='?',
                        help='Minimum observation it must have made')
    parser.add_argument('handles', default='n', nargs='?',
                        help='Add <s> </s> handles to output')
    args = parser.parse_args()

    if args.filename is not None:
        r = Reader(args.filename)
        sentences = r.get_sentences
        m = Markov()

        for sent in sentences:  # for each sentence
            sent[len(sent)-1] = sent[len(sent)-1].rstrip('\n')
            m.add_chain(sent)  # build chain out of words

        if args.handles is 'y':
            print("<s> ", end="")
            m.traverse(args.eta_s, args.minlen)
            print("<\s>")
        else:
            m.traverse(args.eta_s, args.minlen)
            print("")
    else:
        print("No filename")
