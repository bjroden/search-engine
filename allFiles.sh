#!/bin/bash
#!/usr/bin/python3

python3 hw1.py "$1" "$2"
sort -nr $2/sortedFrequency.txt -o $2/sortedFrequency.txt
sort -d $2/sortedToken.txt -o $2/sortedToken.txt
echo "Sorting finished"