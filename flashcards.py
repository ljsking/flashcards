import urllib2
import sqlite3
from flask import Flask, g, render_template, redirect, url_for

def get_img(name):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    infile = opener.open('http://en.wikipedia.org/w/index.php?title=%s&printable=yes'%name)
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(infile.read())
    tbl = soup.find('table', 'infobox')
    img = tbl.find('img')['src']
    desc = tbl.find(text="IUPAC").findParent('tr').findNext('tr').find('td').text
    #desc = '7-Chloro-3-hydroxy-5-phenyl-1,3-dihydro-1,4-benzodiazepin-2-one'
    return img, desc

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
def index():
    return render_template("index.html")

@app.route("/structure")
@app.route("/structure/<int:page>")
def structure(page=0):
    if page == 0:
        q = "SELECT * FROM items ORDER BY RANDOM() limit 25;"
    else:
        q = "SELECT * FROM items limit %d offset %d ;"%(50, (page-1)*50)
    rz = query_db(q)
    return render_template("card.html", cards=rz)
    
@app.route("/iupac")
@app.route("/iupac/<int:page>")
def iupac(page=0):
    if page == 0:
        q = "SELECT * FROM items ORDER BY RANDOM() limit 25;"
    else:
        q = "SELECT * FROM items limit %d offset %d ;"%(50, (page-1)*50)
    rz = query_db(q)
    return render_template("card2.html", cards=rz)

@app.route("/show/<name>")
def show(name):
    q = "SELECT * FROM items WHERE name=?"
    rz = query_db(q, (name,), one=True)
    return "<h2>%s</h2><img src='%s'/><p>%s</p>"%(rz['name'], rz['img'], rz['desc'])

@app.route("/list")
def list():
    q = "SELECT name FROM items"
    rz = query_db(q)
    return render_template("list.html", items=rz)
    
@app.route("/insert/<name>")
def insert(name):
    img, desc = get_img(name)
    try:
        g.db.execute('insert into items (name, img, desc) VALUES (?, ?, ?)', (name, img, desc))
    except sqlite3.IntegrityError:
        g.db.execute('update items set img=?, desc=? where name=?', (img, desc, name))
    g.db.commit()
    return 'ok'
    
@app.route("/delete/<name>")
def delete(name):
    try:
        g.db.execute('delete from items where name = "%s"'%name)
    except sqlite3.IntegrityError:
        logging.exception('')
    g.db.commit()
    return redirect(url_for('list'))
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)