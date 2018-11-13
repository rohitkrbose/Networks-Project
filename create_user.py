import hashlib
import getpass
import sqlite3
import sys

def create (email,pw):
	connection = sqlite3.connect("back.db")
	cur = connection.cursor()

	# Check if exists
	comm = 'SELECT * FROM USER WHERE email=' + '\"' + email + '\"' 
	cur.execute(comm)
	res = cur.fetchall()
	if (len(res) != 0):
		print ('E-mail already exists!')
		return (False)

	# Email does not exist
	hash_obj = hashlib.md5(pw.encode('utf-8'))
	pw_hash = hash_obj.hexdigest()
	comm = 'INSERT INTO USER VALUES(' + '\"' + email + '\"' + ',' + '\"' + pw_hash + '\"' + ');'
	cur.execute(comm)
	connection.commit()
	connection.close() 
	return (True)

if __name__ == '__main__':
	email = input("Enter e-mail: ")
	pw = getpass.getpass('Password: ')
	create(email,pw)