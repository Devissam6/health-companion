import sqlite3, sys


if len(sys.argv) != 2:
    print("INCORRECT NUMBER OF ARGUMENTS.")
    print("USAGE: init_db.py [DATABASE FILE]")

elif sys.argv[1][-3:] != ".db":
    print("SPECIFY .db FILE.")
    print("USAGE: init_db.py [DATABASE FILE]")

else:
    con = sqlite3.connect(sys.argv[1])
    with open("schema.sql") as schema:
        con.executescript(schema.read())
    con.close()