from datetime import date
from Model import Model
import sqlite3
DB_FILE = 'entries.db'    # file for our Database

class model(Model):
    def __init__(self):
        # Make sure our database exists
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        try:
            cursor.execute("select count(rowid) from bubbletea")
        except sqlite3.OperationalError:
            cursor.execute("create table bubbletea (name text, address text, city text, state text, zipcode number, signed_on date, message text)")
        cursor.close()

    def select(self):
        """
        Gets all rows from the database
        Each row contains: name, address, state, city, zipcode, date, message
        :return: List of lists containing all rows of database
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bubbletea")
        return cursor.fetchall()

    def insert(self, name, address, city, state, zipcode, message):
        """
        Inserts entry into database
        :param name: String
        :param address: String
	:param city: String
        :param state: String
	:param zipcode: integer
	:param message: String
        :return: True
        :raises: Database errors on connection and insertion
        """
        params = {'name':name, 'address':address, 'city':city, 'state':state, 'zipcode':zipcode, 'signed_on':date.today(), 'message':message}
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("insert into bubbletea (name, address, city, state, zipcode, signed_on, message) VALUES (:name, :address, :city, :state, :zipcode, :signed_on, :message)", params)

        connection.commit()
        cursor.close()
        return True

