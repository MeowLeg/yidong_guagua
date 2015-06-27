import sqlite3

db = sqlite3.connect("/home/zsgd/yidong/middle.db")
cur = db.cursor()

cur.execute("update flows set left = 3")
db.commit()

print "OK"
