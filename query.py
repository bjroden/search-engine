import sys
import hashlib
from parser import tokenize
from constants import *
import hashtable

def hashfunction(key): # hash function to find the location
    h = hashlib.sha1() # any other algorithm found in hashlib.algorithms_guaranteed can be used here
    h.update(bytes(key, encoding="latin-1"))
    return int(h.hexdigest(), 16) % GLOB_HT_SIZE

def rehash(oldhash): # called when index collision happens, using linear probing
    return (oldhash+3) % GLOB_HT_SIZE

dictFile = open("output/hw4output/dict", 'r')
postFile = open("output/hw4output/post", 'r')
query = sys.argv[1]

tokens = tokenize(query)
dictRecords = []
for i in tokens:
    hash = hashfunction(i)
    dictFile.seek(hash * DICT_RECORD_SIZE)
    record = dictFile.read(DICT_RECORD_SIZE - 1).split() # -1 for newline character
    while record[0] != i and record[0] != "!NULL":
        hash = rehash(hash)
        dictFile.seek(hash * DICT_RECORD_SIZE)
        record = dictFile.read(DICT_RECORD_SIZE - 1).split() # -1 for newline character
    if record[0][0] != "!":
        dictRecords += [record]

expectedDocs = 0
for i in dictRecords:
    expectedDocs += int(i[1])
queryHT = hashtable.HashTable(expectedDocs * 3)

for i in dictRecords:
    term = i[0]
    numdocs = int(i[1])
    start = int(i[2])
    postFile.seek(start * POST_RECORD_SIZE)
    for j in range(numdocs):
        postrecord = postFile.read(POST_RECORD_SIZE - 1).split()
        queryHT.insert(postrecord[0], int(postrecord[1]))
        postFile.read(1)