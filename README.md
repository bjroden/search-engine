# Information Retrieval Search Engine

Programs to tokenize a directory of files (html expected), create an inverted file mapping to show which documents that terms are contained in, and process search queries to return the most relevant files for given tokens.

tokenize_directory.py tokenizes a directory of files and creates dict, post, and map files in the given output directory. query.py uses these to search for which documents are most relevant to a user query.