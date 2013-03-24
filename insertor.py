import sys
import flashcards
import sqlite3
import logging

db = sqlite3.connect(flashcards.DATABASE)

for line in sys.stdin:
	name = line.strip()
	try:
		img, desc = flashcards.get_img(name)
		try:
		    db.execute('insert into items (name, img, desc) VALUES (?, ?, ?)', (name, img, desc))
		except sqlite3.IntegrityError:
		    db.execute('update items set img=?, desc=? where name=?', (img, desc, name))
	except:
		logging.exception('error')
		print name
db.commit()