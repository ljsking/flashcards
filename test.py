import urllib2
import sqlite3
from flask import Flask, g

def get_img(name):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    infile = opener.open('http://en.wikipedia.org/w/index.php?title=%s&printable=yes'%name)
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(infile.read())
    return soup.find('table', 'infobox').find('img')


app = Flask(__name__)

import os
DATABASE = os.path.abspath(os.path.join(__file__, '..', 'database.db'))

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/<name>")
def hello(name):
    return str(get_img(name))
    
if __name__ == "__main__":
    app.run(debug=True)