import bisect
from functools import reduce
from operator import add
from typing import List, TextIO
from classes import DictRecord, QueryResult
from parser import tokenize
from constants import *
from hashtable import HashTable, hashfunction, rehash
from classes import DictRecord
import argparse

def getQueryTokens(query: List[str]) -> List[str]:
    tokens = reduce(add, [tokenize(q) for q in query])
    return tokens

def getDictRecords(tokens: List[str], dictFile: TextIO) -> List[DictRecord]:
    # Search dict file for each token
    dictRecords: List[DictRecord] = []
    for i in tokens:
        # Read dict record from byte offset
        hash = hashfunction(i, GLOB_HT_SIZE)
        dictFile.seek(hash * DICT_RECORD_SIZE)
        term, numDocs, postLineStart  = tuple(dictFile.read(DICT_RECORD_SIZE - 1).split()) # -1 for newline character
        record = DictRecord(term, int(numDocs), int(postLineStart))
        # Rehash for collisions
        while record.term != i and record.term != "!NULL":
            hash = rehash(hash, GLOB_HT_SIZE)
            dictFile.seek(hash * DICT_RECORD_SIZE)
            term, numDocs, postLineStart  = tuple(dictFile.read(DICT_RECORD_SIZE - 1).split()) # -1 for newline character
            record = DictRecord(term, int(numDocs), int(postLineStart))
        # Ignore !NULL and !DELETED
        if not record.term.startswith("!"):
            dictRecords += [record]
    return dictRecords

def makeQueryHT(dictRecords: List[DictRecord], postFile: TextIO) -> HashTable[int]:
    # Create hashtable for doc weights, with size = 3 * sum(all numdocs values for each dict record) for more efficient memory usage
    expectedDocs = sum(r.numDocs for r in dictRecords)
    queryHT = HashTable[int](expectedDocs * 3)

    # Calculate doc weights
    for r in dictRecords:
        postFile.seek(r.postLineStart * POST_RECORD_SIZE)
        # For each posting, add the weight to the appropriate queryHT bucket
        for _ in range(r.numDocs):
            docID, weight = tuple(postFile.read(POST_RECORD_SIZE).split())
            queryHT.insert(docID, int(weight))
    return queryHT

def getSortedResults(queryHT: HashTable[int], numResults: int) -> List[QueryResult]:
    # Sort results with a minheap where max size = numResults
    sortedResults: List[QueryResult] = []
    for docID, weight in zip(queryHT.slots, queryHT.data):
        if docID and weight and weight:
            bisect.insort_right(sortedResults, QueryResult(int(docID), weight), key=lambda x: -1 * x.weight)
            sortedResults = sortedResults[:numResults]
    return sortedResults

def displaySortedResults(sortedResults: List[QueryResult], mapFile: TextIO):
    for i, result in enumerate(sortedResults, 1):
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
        displaySortedResults(sortedResults, mapFile)
            
    
if __name__ == "__main__":
    main()