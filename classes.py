from collections import deque
from dataclasses import dataclass
from functools import total_ordering
from typing import Deque

@dataclass
class DictRecord:
    term: str
    numDocs: int
    postLineStart: int

@dataclass 
class PostRecord:
    docID: int
    rtf: int

class GlobHTEntry:
    numDocs: int
    totalFreq: int
    files: Deque[PostRecord]

    def __init__(self, totalFreq: int, data: PostRecord):
        self.numDocs = 1
        self.totalFreq = totalFreq
        self.files = deque()
        self.files.append(data)
    
    def __add__(self, other: 'GlobHTEntry'):
        self.numDocs += other.numDocs
        self.totalFreq += other.totalFreq
        self.files += other.files
        return self

@dataclass 
@total_ordering
class QueryResult:
    docID: int
    weight: int

    def __le__(self, other: 'QueryResult'):
        return self.weight < other.weight

    def __eq__(self, other: 'QueryResult'):
        return self.weight == other.weight