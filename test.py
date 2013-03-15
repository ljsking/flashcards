import urllib2
import sqlite3
from flask import Flask, g

def get_img(name):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    infile = opener.open('http://en.wikipedia.org/w/index.php?title=%s&printable=yes'%name)
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(infile.read())
    return soup.find('table', 'infobox').find('img')['src']


app = Flask(__name__)

import os
DATABASE = os.path.abspath(os.path.join(__file__, '..', 'database.db'))

def connect_db():
    return sqlite3.connect(DATABASE)
    
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/")
def hello():
    q = "SELECT * FROM items ORDER BY RANDOM() LIMIT 1;"
    rz = query_db(q, one=True)
    return "<h2>%s</h2><img src='%s'/>"%(rz['name'], rz['img'])
    
@app.route("/insert/<name>")
def insert(name):
    img=str(get_img(name))
    g.db.execute('insert into items (name, img) VALUES (?, ?)', (name, img))
    g.db.commit()
    return 'ok'
    
if __name__ == "__main__":
    app.run(debug=True)