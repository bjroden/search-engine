# Given an input directory and output directory from the command line, tokenize a directory of files and create inverted files

import hashtable
from parser import tokenize
from constants import *
import sys
import os
import math
from collections import Counter, namedtuple

# Returns string of numchars length, truncated if len(string) > numchars, or padded with spaces if len(string) < numchars
def fixLength(string, numchars):
    return string.ljust(numchars)[:numchars]

def dictWrite(dictFile, term, numDocs, postLineNo):
    termString = fixLength(str(term), TERM_LENGTH)
    numDocsString = fixLength(str(numDocs), NUMDOCS_LENGTH)
    postLineNoString = fixLength(str(postLineNo), START_LENGTH)
    dictFile.write(f"{termString} {numDocsString} {postLineNoString}\n")

def postWrite(postFile, docOccurrence, idf):
    tf = docOccurrence.tf
    docIDString = fixLength(str(docOccurrence.docID), DOCID_LENGTH)
    weightString = fixLength(str(int(tf * idf * 100000000)), WEIGHT_LENGTH)
    postFile.write(f"{docIDString} {weightString}\n")

# Open file directories
indir = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])
if not os.path.isdir(indir):
    print("Error: invalid input path")
    exit()
if not os.path.isdir(outdir):
    print("Error: invalid output path")
    exit()
try:
    dictFile = open("{}/dict".format(outdir), 'w')
    postFile = open("{}/post".format(outdir), 'w')
    mapFile = open("{}/map".format(outdir), 'w')
except Exception as e:
    print("Error opening output files: {}", str(e))
    exit()

# Format that global hashtable records are entered in
PostRecord = namedtuple('PostRecord', 'docID tf')
EntryRecord = namedtuple('EntryRecord', 'totalFreq, postrecord')

# Initialize values
totalTokens = 0 
docID = 0
docHT = hashtable.HashTable(DOC_HT_SIZE)
globHT = hashtable.GlobalHashTable(GLOB_HT_SIZE)
# Create stopword hashtable
try:
    stopFile = open("stopwords").read()
except Exception as e:
    print("Error opening stopfile: {}".format(str(e)))
    exit()
stopHT = hashtable.HashTable(STOP_HT_SIZE)
for t in tokenize(stopFile):
    # Get every token in the "stopwords" file and add them to the stopword hashtable
    if len(t) > 1:
        stopHT.insert(t, 1)

# Tokenize every file in indir
for i in os.listdir(indir):
    # Open current input file
    try:
        data = open("{}/{}".format(indir, i), 'r', encoding="latin-1").read()
    except Exception as e:
        print("Error opening file {}: {}".format(), i, str(e))
        continue
    
    # Read tokens and add them to document hashTable
    docTokens = 0
    for t in tokenize(data):
        if len(t) > 1 and not stopHT.intable(t):
            docHT.insert(t, 1)
    # Write doc HT to global HT, reset docHT, and write filename to map file
    for j in range(DOC_HT_SIZE):
        term = docHT.slots[j]
        freq = docHT.data[j]
        if term is not None and freq != 0:
           rtf = freq / docHT.totalTokens
           globHT.insert(term, EntryRecord(freq, PostRecord(docID, rtf)))
    docHT.reset()
    mapFile.write("{}\n".format(i.ljust(MAPNAME_LENGTH)))
    docID += 1

# Write all entries to the dict and post files
postLineNo = 0
totalDocs = docID
for i in range(GLOB_HT_SIZE):
    term = globHT.slots[i]
    bucket = globHT.data[i]
    if term is not None and bucket is not None:
        if bucket.numDocs == 1 and bucket.totalFreq == 1:
            dictWrite(dictFile, "!DELETED", "-1", "-1")
        else:
            # Create fixed-length strings and write to dict
            dictWrite(dictFile, term, bucket.numDocs, postLineNo)
            # Write fixed-length docID and term weights to post file
            idf = 1 + math.log(totalDocs / bucket.numDocs, 10)
            for docOccurrence in bucket.files:
                postWrite(postFile, docOccurrence, idf)
                postLineNo += 1
    # Fixed-length null bucket for dict file
    else:
        dictWrite(dictFile, "!NULL", "-1", "-1")