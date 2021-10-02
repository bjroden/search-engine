# Information Retrieval Homework 1
# Author: Brian Roden
# Program to parse html files for tokens

from hashtable import HashTable
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

# Regex checks for hyperlinks, which are words starting with http://, https://, or www., and any number of non-whitespace, html tags, or "/" is found (since including the specific subdirectory of the site is not useful for indexing)
# The starting elements are then scrubbed out
def t_HYPERLINK(t):
    r'(htt(p|ps):\/\/|www.)[^\s<\/]+'
    t.value = t.value.lower()
    t.value = re.sub(r'(https://|http://|www|\.)', '', t.value)
    return t

# Regex to check for emails, which take the form "word@word.word"
# HTML tags and everything following @ is removed since searching for "gmail" to get a specific email address is unlikely
def t_EMAIL(t):
    r'\S+@\S+\.[^<\s,?!.\xa0\x85]+'
    t.value = re.sub('(@.*|<[^>]+>)', '', t.value)
    return t

# Regex to check for numbers, which include commas, decimals, and hyphens for phone numbers
# Will not start with 0 since "01" and "1" should be the same in searches. Commas and hyphens are removed, as well as everything following the decimal since a search for "20.07" specifically would likely not be useful
def t_NUMBER(t):
    r'[1-9](\d|,|\.|-)*'
    t.value = re.sub('(,|-|\.\S*)', '', t.value)
    return t

# Regex to remove common html entities like "&nbsp" which the parser was otherwise unable to detect
# No return statement because these are not useful for indexing
def t_HTML_ENTITY(t):
    r'\&\w+'

# Words are similar to typical IDs, exxcept with special inclusions for allowing specific punctuation so tokens don't become improperly split.
# These start with a A-z character, and can be followed by more characters, digits, hyphens, apostrophes, html tags, and periods for abbreviations like "PH.D"
# These additions are included since "we'll" won't become "we" and "ll" separately, nor "<b>E</b>lephants" becoming "e" and "lephants". These are then removed with the re.sub expression to make for better indexing
# Other punctuation marks, like ?, !, etc. are not typically connecting words together, so these are not included
def t_WORD(t):
    r'[A-z](\w|\'|-|\.\w|<[^>]+>)*'
    t.value = t.value.lower()
    t.value = re.sub('(\.|-|\'|<[^>]+>)', '', t.value)
    return t

# Tracks line numbers with \n. Mostly for debugging purposes, but it's inclusion does not hurt performance.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore these characters if they are not already a token. Improves performance since these won't have to be passed through the regex rules.
t_ignore  = ' []+$|=%*{}/0-"#>();:!?.,\t\xa0\x85\xe2\x00'

# Skips letters that fail all token checks. Punctuation like & and < will use this a lot: they cannot be included in t_ignore since they are required for the start of some regex rules.
def t_error(t):
    t.lexer.skip(1)

# Create the parser
lexer = lex.lex()

# Open file directories
indir = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])
if not os.path.isdir(indir):
    print("Error: invalid input path")
    exit()
if not os.path.isdir(outdir):
    print("Error: invalid output path")
    exit()
# Make directory for tokenized files
try:
    os.mkdir("{}/fileCounts".format(outdir))
except FileExistsError:
    pass
except Exception as e:
    print("Error opening file: {}".format(e))
    exit()

# Initialize values
totalTokens = 0 
docHT = HashTable(50000)
# Tokenize every file in indir
for i in os.listdir(indir):
    # Open current input file and corresponding output file
    try:
        data = open("{}/{}".format(indir, i), 'r', encoding="latin-1").read()
        lexer.input(data)
        outputFile = open("{}/fileCounts/{}.txt".format(outdir, i), 'w')
    except Exception as e:
        print("Error opening file {}: {}".format(), i, str(e))
        continue
    
    # Read tokens, add them to document hashTable, and increment counts
    docTokens = 0
    while True:
        tok = lexer.token()
        if not tok:
            break
        docHT.insert(tok.value, 1)
        docTokens += 1
    totalTokens += docTokens
    # Write number of unique and total tokens to file, reset document hashtable to 0s
    outputFile.write("File: {}\nUnique: {:n}\nTotal: {:n}".format(i, docHT.uniqueTokens, docTokens))
    docHT.reset()

# Write total token count to stdout
open("{}/total.txt".format(outdir), 'w').write("\nTotal tokens: {:n}".format(totalTokens))