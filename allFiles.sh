#!/bin/bash
#!/usr/bin/python3
for f in files/*; do python3 tokenTest.py $f > "/output/$f.txt"; done
