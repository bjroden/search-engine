import bisect
from functools import reduce
import json
from operator import add
from typing import List, TextIO
from classes import DictRecord, QueryResult
from parser import tokenize
from constants import *
from hashtable import HashTable, hashfunction, rehash
from classes import DictRecord

def _getQueryTokens(query: List[str]) -> List[str]:
    tokens = reduce(add, [tokenize(q) for q in query])
    return tokens

def _getDictRecords(tokens: List[str], dictFile: TextIO) -> List[DictRecord]:
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

def _makeQueryHT(dictRecords: List[DictRecord], postFile: TextIO) -> HashTable[int]:
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

def _getSortedResults(queryHT: HashTable[int], numResults: int) -> List[QueryResult]:
    # Sort results with a minheap where max size = numResults
    sortedResults: List[QueryResult] = []
    for docID, weight in zip(queryHT.slots, queryHT.data):
        if docID and weight and weight:
            bisect.insort_right(sortedResults, QueryResult(int(docID), weight), key=lambda x: -1 * x.weight)
            sortedResults = sortedResults[:numResults]
    return sortedResults

def _getJson(sortedResults: List[QueryResult], mapFile: TextIO):
    output = []
    for i, result in enumerate(sortedResults, 1):
        mapFile.seek(result.docID * MAP_FILE_SIZE) 
        mapName = mapFile.read(MAP_FILE_SIZE - 1)
        output.append({"ranking": i, "fileName": mapName, "weight": result.weight})
    return json.dumps(output)

def makeSearch(query: str, numResults: int, indir: str) -> str:
    # Open files
    with (
        open(f"{indir}/dict", 'r') as dictFile,
        open(f"{indir}/post", 'r') as postFile,
        open(f"{indir}/map", 'r') as mapFile,
    ):
        tokens = _getQueryTokens([query])
        dictRecords = _getDictRecords(tokens, dictFile)
        queryHT = _makeQueryHT(dictRecords, postFile)
        sortedResults = _getSortedResults(queryHT, numResults)
        return _getJson(sortedResults, mapFile)
            