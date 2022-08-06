from flask import Flask, request
from query import makeSearch

app = Flask(__name__)

@app.route("/")
def hello():
    return makeSearch(request.args.get('query'), 10, 'output/this-output')