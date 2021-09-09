# ------------------------------------------------------------
 # calclex.py
 #
 # tokenizer for a simple expression evaluator for
 # numbers and +,-,*,/
 # ------------------------------------------------------------
import ply.lex as lex
import sys
import re
from collections import Counter

# List of token names.   This is always required
tokens = (
   'HTMLTAG',
   'HYPERLINK',
   'EMAIL',
   'NUMBER',
   'WORD',
)

def t_HTMLTAG(t):
    r'<[^>]+>'
    #r'<.+?(?=>)>'
    #return t

def t_HYPERLINK(t):
    r'(htt(p|ps):\/\/|www.)[^\s<]+'
    #TODO: less bad
    t.value = t.value.lower()
    t.value = re.sub(r'(https://|http://|www|\.)', '', t.value)
    return t

def t_EMAIL(t):
    r'\S+@\S+\.[^<\s,?!.\xa0\x85]+'
    return t

def t_NUMBER(t):
    r'\d+'
    return t

def t_WORD(t):
    # Match non whitespace character followed by any number of non-< characters, followed by a non-punctuation mark
    r'(\S(?!<))*[^<\s,?!.\xa0\x85]'
    t.value = t.value.lower()
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' !?.,\t\xa0\x85'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

allTokens = Counter({})
for i in sys.argv[1:]:
    try:
        data = open(i, 'r', encoding="latin-1").read()
        lexer.input(data)
    except Exception as e:
        print("Error opening file " + i + ": " + str(e))
        continue
    currentTokens = Counter({})
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break
        allTokens[tok.value] += 1
        currentTokens[tok.value] += 1
    outputFile = open("output/" + i + ".txt", 'w')
    for j in currentTokens:
        outputFile.write(str(currentTokens[j]) + '\t' + j + '\n')

sortedToken = open("output/sortedToken.txt", 'w')
sortedFrequency = open("output/sortedFrequency.txt", 'w')
for i in allTokens:
    sortedToken.write(i + '\t' + str(allTokens[i]) + '\n')
    sortedFrequency.write(str(allTokens[i]) + '\t' + i + '\n')


print("Python script finished")