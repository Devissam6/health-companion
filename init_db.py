import sqlite3

con = sqlite3.connect('foodData.db')

with open('schema.sql') as schema:
    con.executescript(schema.read())

con.close()