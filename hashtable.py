# Created by Ang Li
# October 2, 2016
# Modified by Marion Chiariglione
# September 22, 2018
import hashlib
from typing import Generic, List, TypeVar

def hashfunction(key: str, size: int) -> int: # hash function to find the location
    h = hashlib.sha1() # any other algorithm found in hashlib.algorithms_guaranteed can be used here
    h.update(bytes(key, encoding="latin-1"))
    return int(h.hexdigest(), 16)%size

def rehash(oldhash: int, size: int) -> int: # called when index collision happens, using linear probing
    return (oldhash+3)%size

T = TypeVar("T")
class HashTable(Generic[T]):
    size: int
    uniqueTokens: int
    totalTokens: int
    slots: List[str | None]
    data: List[T | None]

    def __init__(self, table_size: int):
        self.size=table_size # size of hash table
        self.uniqueTokens=0
        self.totalTokens=0
        self.slots=[None]*self.size # initialize keys
        self.data=[None]*self.size # initialize values
    
    def reset(self): # reset keys without creating new HT
        self.uniqueTokens=0
        self.totalTokens=0
        self.slots=[None]*self.size # initialize keys
    
    def hashfunction(self,key: str) -> int: # hash function to find the location
        return hashfunction(key, self.size)

    def rehash(self, oldhash: int) -> int: # called when index collision happens, using linear probing
        return rehash(oldhash, self.size)

    def insert(self, key: str, data: T): # insert k,v to the hash table
        hashvalue = self.hashfunction(key)  # location to insert
        if self.slots[hashvalue] == None:
            self.slots[hashvalue] = key
            self.data[hashvalue] = data
            self.uniqueTokens += 1
        else:
            if self.slots[hashvalue] == key:  # key already exists, update the value
                self.data[hashvalue] += data
            else:
                nextslot=self.rehash(hashvalue) # index collision, using linear probing to find the location
                if self.slots[nextslot] == None:
                    self.slots[nextslot] = key
                    self.data[nextslot] = data
                    self.uniqueTokens += 1
                elif self.slots[nextslot] == key:
                    self.data[nextslot] += data
                else:
                    while self.slots[nextslot] != None and self.slots[nextslot] != key:
                        nextslot=self.rehash(nextslot)
                        if self.slots[nextslot] == None:
                            self.slots[nextslot] = key
                            self.data[nextslot] = data
                            self.uniqueTokens += 1

                        elif self.slots[nextslot] == key:
                            self.data[nextslot] += data
        self.totalTokens+=1

    def get(self, key: str) -> T:  # get the value by looking for the key
        startslot = self.hashfunction(key)
        data = None
        stop = False
        found = False
        position = startslot
        while self.slots[position] != None and not found and not stop:
            if self.slots[position] == key:
                found = True
                data = self.data[position]
            else:
                position=self.rehash(position)
                if position == startslot:
                    stop = True
        return data

    def intable(self, key: str) -> bool:  # determine whether a key is in the hash table or not
        startslot = self.hashfunction(key)
        stop = False
        found = False
        position = startslot
        while self.slots[position] != None and not found and not stop:
            if self.slots[position] == key:
                found = True
            else:
                position=self.rehash(position)
                if position == startslot:
                    stop = True
        return found

    def __getitem__(self, key: str) -> T:
        return self.get(key)

    def __setitem__(self, key: str, data: T):
        self.insert(key,data)

    def __len__(self) -> int:
        return self.size
