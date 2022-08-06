# Given an input directory and output directory from the command line, tokenize a directory of files and create inverted files

from typing import Tuple
from hashtable import HashTable, PostRecord, EntryRecord
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

def populateStopHT(stopFile) -> HashTable:
    stopHT = HashTable(STOP_HT_SIZE)
    for token in tokenize(stopFile):
        # Get every token in the "stopwords" file and add them to the stopword hashtable
        if len(token) > 1:
            stopHT.insert(token, 1)
    return stopHT

def postWrite(postFile, docOccurrence, idf):
    tf = docOccurrence.rtf
    docIDString = fixLength(str(docOccurrence.docID), DOCID_LENGTH)
    weightString = fixLength(str(int(tf * idf * 100000000)), WEIGHT_LENGTH)
    postFile.write(f"{docIDString} {weightString}\n")

def tokenizeFiles(indir, stopHT, mapFile) -> Tuple[int, HashTable]:
    currentDocNo = 0
    docHT = HashTable(DOC_HT_SIZE)
    globHT = HashTable(GLOB_HT_SIZE)
    # Tokenize every file in indir
    for fileName in os.listdir(indir):
        with open(f"{indir}/{fileName}", 'r', encoding="latin-1") as file:
            data = file.read()
            # Read tokens and add them to document hashTable
            for t in tokenize(data):
                if len(t) > 1 and not stopHT.intable(t):
                    docHT.insert(t, 1)
            # Write doc HT to global HT, reset docHT, and write filename to map file
            for term, freq in zip(docHT.slots, docHT.data):
                if term is not None and freq != 0:
                    rtf = freq / docHT.totalTokens
                    globHT.insert(term, EntryRecord(freq, PostRecord(currentDocNo, rtf)))
            docHT.reset() 
            mapFile.write("{}\n".format(fileName.ljust(MAPNAME_LENGTH)))
            currentDocNo += 1
    return (currentDocNo, globHT)

def writeFiles(totalDocs, globHT, dictFile, postFile):
    # Write all entries to the dict and post files
    postLineNo = 0
    for term, bucket in zip(globHT.slots, globHT.data):
        if term is None or bucket is None:
            # Fixed-length null bucket for dict file else:
            dictWrite(dictFile, "!NULL", "-1", "-1")
        elif bucket.numDocs == 1 and bucket.totalFreq == 1:
            # Fixed-length deleted bucket for dict file else:
            dictWrite(dictFile, "!DELETED", "-1", "-1")
        else:
            # Create fixed-length strings and write to dict
            dictWrite(dictFile, term, bucket.numDocs, postLineNo)
            # Write fixed-length docID and term weights to post file
            idf = 1 + math.log(totalDocs / bucket.numDocs, 10)
            for docOccurrence in bucket.files:
                postWrite(postFile, docOccurrence, idf)
                postLineNo += 1

def main():
    # Open file directories
    indir = os.path.abspath(sys.argv[1])
    outdir = os.path.abspath(sys.argv[2])
    if not os.path.isdir(indir):
        print("Error: invalid input path")
        exit()
    if not os.path.isdir(outdir):
        print("Error: invalid output path")
        exit()

    # Create stopword hashtable
    with open("stopwords", 'r') as stopFile:
        stopHT = populateStopHT(stopFile.read())
    
    with (
        open(f"{outdir}/dict", 'w') as dictFile,
        open(f"{outdir}/post", 'w') as postFile,
        open(f"{outdir}/map", 'w') as mapFile,
    ):
        totalDocs, globHT = tokenizeFiles(indir, stopHT, mapFile)
        writeFiles(totalDocs, globHT, dictFile, postFile)

if __name__ == "__main__":
    main()