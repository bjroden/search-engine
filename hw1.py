# Information Retrieval Homework 1
# Author: Brian Roden
# Program to parse files for tokens

import ply.lex as lex
import sys
import re
import os
from collections import Counter

# List of token types
tokens = (
    'CSS',
    'HTMLTAG',
    'HYPERLINK',
    'EMAIL',
    'NUMBER',
    'HTML_ENTITY',
    'WORD',
)

# CSS Tags take the form: element1, element2, .. elementN { ** CSS ** }
# Regex Checks for any amount of words with a comma, followed by another word, followed by { ** CSS ** }
# No return statement because these are not useful for indexing
def t_CSS(T):
    r'([\S^,]*,\s*)*\S+\s*{[^}]+}'

# HTML Elements take the forms <! **** COMMENT / DOCTYPE ****>, or <WORD attribute1=value attribute2=value>, or </WORD>
# Regex first checks for a "<", then first checks if there is a "!" character, in which case it will read until the next ">", since these are either comments or DOCTYPE declarations.
# If no "!", it will look for "<" followed by an optional "/", followd by WORD, followed by any amount of "attribute=value", followed by optional whitespace, then ">"
# No return statement because these are not useful for indexing
def t_HTMLTAG(t):
    r'<(![^>]+|\/?\w+((\s*[^\s=>])+=(\s*[^\s=>])+)*\s*\/?)>'

# Regex checks for hyperlinks, which are words starting with http://, https://, or www., and any number of non-whitespace or htmltags following that
# These starting elements are then scrubbed out
def t_HYPERLINK(t):
    r'(htt(p|ps):\/\/|www.)[^\s<]+'
    t.value = t.value.lower()
    t.value = re.sub(r'(https://|http://|www|\.)', '', t.value)
    return t

# Regex to check for emails, which take the form "word@word.word"
def t_EMAIL(t):
    r'\S+@\S+\.[^<\s,?!.\xa0\x85]+'
    t.value = re.sub('(@.*|<[^>]+>)', '', t.value)
    return t

# Regex to check for numbers, which include commas, decimals, and hyphens for phone numbers and then scrubs these elements out
def t_NUMBER(t):
    r'(\d|,|\.|-)+'
    t.value = re.sub('(,|\.|-)', '', t.value)
    return t

# Regex to remove common html entities which the parser was otherwise unable to detect
# No return statement because these are not useful for indexing
def t_HTML_ENTITY(t):
    r'\&\w+'

# TODO: Figure this out
def t_WORD(t):
    r'\w(\w|\'|-|<[^>]+>)*'
    t.value = t.value.lower()
    t.value = re.sub('(-|\'|<[^>]+>)', '', t.value)
    return t

# TODO: Tracks line numbers for debugging
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore these characters if they are not already part of an expression
t_ignore  = ' -"#>();:!?.,\t\xa0\x85\xe2\x00'

# TODO: Remove this
def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Create the parser
lexer = lex.lex()

#Open paths
indir = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])
if not os.path.isdir(indir):
    print("Error: invalid input path")
    exit()
if not os.path.isdir(outdir):
    print("Error: invalid output path")
    exit()

# allTokens will be where all tokens are stored
allTokens = Counter({})
for i in os.listdir(indir):
    # Open all files passed as parameters
    try:
        data = open(indir + "/" + i, 'r', encoding="latin-1").read()
        lexer.input(data)
    except Exception as e:
        print("Error opening file " + i + ": " + str(e))
        continue

    # CurrentTokens is like alltokens, but only for the current file
    currentTokens = Counter({})
    while True:
        # Read a token and add it to both allTokens and currentTokens
        tok = lexer.token()
        if not tok:
            break
        allTokens[tok.value] += 1
        currentTokens[tok.value] += 1
    # Write all current tokens to a file
    try:
        outputFile = open(outdir + "/" + i + ".txt", 'w')
        for j in currentTokens:
                outputFile.write(str(currentTokens[j]) + '\t' + j + '\n')
    except Exception as e:
        print("Error writing to file " + j + ": " + str(e))

# Write all tokens to two separate files. These will be sorted by the bash script.
sortedToken = open(outdir + "/sortedToken.txt", 'w')
sortedFrequency = open(outdir + "/sortedFrequency.txt", 'w')
for i in allTokens:
    sortedToken.write(i + '\t' + str(allTokens[i]) + '\n')
    sortedFrequency.write(str(allTokens[i]) + '\t' + i + '\n')


print("Python script finished")
