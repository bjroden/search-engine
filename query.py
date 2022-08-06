import hashlib
from typing import List, TextIO
from classes import DictRecord, QueryResult
from parser import tokenize
from constants import *
from hashtable import HashTable
from classes import PostRecord, DictRecord
import heapq
import argparse

def hashfunction(key: str) -> int: # hash function to find the location
    h = hashlib.sha1() # any other algorithm found in hashlib.algorithms_guaranteed can be used here
    h.update(bytes(key, encoding="latin-1"))
    return int(h.hexdigest(), 16) % GLOB_HT_SIZE

def rehash(oldhash: int) -> int: # called when index collision happens, using linear probing
    return (oldhash+3) % GLOB_HT_SIZE

def getQueryTokens(query: List[str]) -> List[str]:
    # Tokenize query terms to match dict file
    tokens = []
    for i in query:
        tokens += tokenize(i)
    return tokens

def getDictRecords(tokens: List[str], dictFile: TextIO) -> List[PostRecord]:
    # Search dict file for each token
    dictRecords: List[DictRecord] = []
    for i in tokens:
        # Read dict record from byte offset
        hash = hashfunction(i)
        dictFile.seek(hash * DICT_RECORD_SIZE)
        term, numDocs, postLineStart  = tuple(dictFile.read(DICT_RECORD_SIZE - 1).split()) # -1 for newline character
        record = DictRecord(term, int(numDocs), int(postLineStart))
        # Rehash for collisions
        while record.term != i and record.term != "!NULL":
            hash = rehash(hash)
            dictFile.seek(hash * DICT_RECORD_SIZE)
            term, numDocs, postLineStart  = tuple(dictFile.read(DICT_RECORD_SIZE - 1).split()) # -1 for newline character
            record = DictRecord(term, int(numDocs), int(postLineStart))
        # Ignore !NULL and !DELETED
        if not record.term.startswith("!"):
            dictRecords += [record]
    return dictRecords

def makeQueryHT(dictRecords: List[DictRecord], postFile: TextIO) -> HashTable[int]:
    # Create hashtable for doc weights, with size = 3 * sum(all numdocs values for each dict record) for more efficient memory usage
    expectedDocs = 0
    for i in dictRecords:
        expectedDocs += i.numDocs
    queryHT = HashTable(expectedDocs * 3)

    # Calculate doc weights
    for i in dictRecords:
        postFile.seek(i.postLineStart * POST_RECORD_SIZE)
        # For each posting, add the weight to the appropriate queryHT bucket
        for j in range(i.numDocs):
            docID, weight = tuple(postFile.read(POST_RECORD_SIZE - 1).split())
            queryHT.insert(docID, int(weight))
            postFile.read(1)
    return queryHT

def getSortedResults(queryHT: HashTable[int], numResults: int) -> List[QueryResult]:
    # Sort results with a minheap where max size = numResults
    sortedResults: List[QueryResult] = []
    i = 0
    # Add to list until capacity
    while i < queryHT.size and len(sortedResults) < numResults:
        if queryHT.slots[i] is not None and queryHT.data[i] is not None:
            docID = int(queryHT.slots[i])
            weight = queryHT.data[i]
            sortedResults += [QueryResult(docID, weight)]
        i += 1
    # Sort that list into heap
    heapq.heapify(sortedResults)
    # Sort remaining results, only push to heap if current queryHT bucket > current minimum sorted result
    while i < queryHT.size:
        if queryHT.slots[i] is not None and queryHT.data[i] is not None:
            docID = int(queryHT.slots[i])
            weight = queryHT.data[i]
            if weight > sortedResults[0].weight:
                heapq.heappushpop(sortedResults, QueryResult(docID, weight))
        i += 1
    return sortedResults

def displaySortedResults(sortedResults: List[QueryResult], mapFile: TextIO, numResults: int):
        # Display results
        if len(sortedResults) < numResults:
            numResults = len(sortedResults)
        else:
            numResults = numResults
        for i in range(numResults, 0, -1):
            result = heapq.heappop(sortedResults)
            mapFile.seek(result.docID * MAP_FILE_SIZE) 
            mapName = mapFile.read(MAP_FILE_SIZE - 1)
            print("{}: {} (weight {})".format(i, mapName, result.weight))

def main():
    # Command line arguments
    argumentparser = argparse.ArgumentParser(description="Given a query and a directory with dict, post, and map files, show which documents are most relevant to the query")
    argumentparser.add_argument('query', nargs='*', help="All args following the query command will be part of the query.")
    argumentparser.add_argument('-d', default="output/hw4output", dest="indir", help="Input directory for dict, post, and map files. Default is output/hw4output.")
    argumentparser.add_argument('-n', type=int, default=10, dest="numResults", help="Show \"numresults\" amount of results for the output. Default is 10.")
    args = argumentparser.parse_args()

    # Open files
    with (
        open(f"{args.indir}/dict", 'r') as dictFile,
        open(f"{args.indir}/post", 'r') as postFile,
        open(f"{args.indir}/map", 'r') as mapFile,
    ):
        tokens = getQueryTokens(args.query)
        dictRecords = getDictRecords(tokens, dictFile)

        # Exit early if no results found
        if len(dictRecords) < 1:
            print("No matches found")
            exit()

        queryHT = makeQueryHT(dictRecords, postFile)
        sortedResults = getSortedResults(queryHT, args.numResults)
        displaySortedResults(sortedResults, mapFile, args.numResults)
            
    
if __name__ == "__main__":
    main()