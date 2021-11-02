import sys
import hashlib
from parser import tokenize
from constants import *
import hashtable
import heapq

def hashfunction(key): # hash function to find the location
    h = hashlib.sha1() # any other algorithm found in hashlib.algorithms_guaranteed can be used here
    h.update(bytes(key, encoding="latin-1"))
    return int(h.hexdigest(), 16) % GLOB_HT_SIZE

def rehash(oldhash): # called when index collision happens, using linear probing
    return (oldhash+3) % GLOB_HT_SIZE

# Open files
dictFile = open("output/hw4output/dict", 'r')
postFile = open("output/hw4output/post", 'r')
mapFile = open("output/hw4output/map", 'r')
query = sys.argv[1]

# Get tokens from input and search dict file for each token
tokens = tokenize(query)
dictRecords = []
for i in tokens:
    # Read dict record from byte offset
    hash = hashfunction(i)
    dictFile.seek(hash * DICT_RECORD_SIZE)
    record = dictFile.read(DICT_RECORD_SIZE - 1).split() # -1 for newline character
    # Rehash for collisions
    while record[0] != i and record[0] != "!NULL":
        hash = rehash(hash)
        dictFile.seek(hash * DICT_RECORD_SIZE)
        record = dictFile.read(DICT_RECORD_SIZE - 1).split() # -1 for newline character
    # Ignore !NULL and !DELETED
    if record[0][0] != "!":
        dictRecords += [record]

# Exit early if no results found
if len(dictRecords) < 1:
    print("No matches found")
    exit()

# Create hashtable for doc weights, with size = 3 * sum(all numdocs values for each dict record) for more efficient memory usage
expectedDocs = 0
for i in dictRecords:
    expectedDocs += int(i[1])
queryHT = hashtable.HashTable(expectedDocs * 3)

# Calculate doc weights
for i in dictRecords:
    term = i[0]
    numdocs = int(i[1])
    start = int(i[2])
    postFile.seek(start * POST_RECORD_SIZE)
    # For each posting, add the weight to the appropriate queryHT bucket
    for j in range(numdocs):
        postrecord = postFile.read(POST_RECORD_SIZE - 1).split()
        queryHT.insert(postrecord[0], int(postrecord[1]))
        postFile.read(1)

# Sort results with a minheap of size QUERY_RESULTS
sortedResults = []
i = 0
# Add to list until capacity
while i < queryHT.size and len(sortedResults) < QUERY_RESULTS:
    if queryHT.slots[i] is not None and queryHT.data[i] is not None:
        docID = queryHT.slots[i]
        weight = queryHT.data[i]
        sortedResults += [(weight, docID)]
    i += 1
# Sort that list into heap
heapq.heapify(sortedResults)
# Sort remaining results, only push to heap if current queryHT bucket > current minimum sorted result
while i < queryHT.size:
    if queryHT.slots[i] is not None and queryHT.data[i] is not None:
        docID = queryHT.slots[i]
        weight = queryHT.data[i]
        if weight > sortedResults[0][0]:
            heapq.heappushpop(sortedResults, (weight, docID))
    i += 1
    
# Display results
if len(sortedResults) < QUERY_RESULTS:
    numResults = len(sortedResults)
else:
    numResults = QUERY_RESULTS
for i in range(numResults, 0, -1):
    result = heapq.heappop(sortedResults)
    weight = result[0]
    docID = int(result[1])
    mapFile.seek(docID * MAP_FILE_SIZE) 
    mapName = mapFile.read(MAP_FILE_SIZE - 1)
    print("{}: {} (weight {})".format(i, mapName, weight))