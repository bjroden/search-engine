#!/bin/bash
#!/usr/bin/python3

python3 hw1.py "$@"
sort -nr output/sortedFrequency.txt -o output/sortedFrequency.txt
sort -d output/sortedToken.txt -o output/sortedToken.txt
echo "Sorting finished"