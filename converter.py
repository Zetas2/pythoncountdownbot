# Handeling the database
import sqlite3

# makes conn_info_db into the connected database.
conn_info_db = sqlite3.connect("Countdowns.db")

conn_info_db.execute("""ALTER TABLE Countdowns ADD COLUMN countdownname varchar(50);""")

"""Yup... All this does is to add a column to a database. 
Dont mind it... It wont be used more than for me to convert 
old databases to new ones with more features"""
