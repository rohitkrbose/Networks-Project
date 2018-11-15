import numpy as np
import hashlib
import getpass
import sqlite3
import smtplib 
import base64
import sys

def verify_mail (email,pw):
	connection = sqlite3.connect("back.db")
	cur = connection.cursor()
	# Check if exists
	comm = 'SELECT * FROM USER WHERE email=' + '\"' + email + '\"' 
	cur.execute(comm)
	res = cur.fetchall()
	if (len(res) == 0):
		# print ('User does not exist!')
		return (False)
	true_pw_hash = res[0][1]
	# Check if password hashes match
	hash_obj = hashlib.md5(pw.encode('utf-8'))
	pw_hash = hash_obj.hexdigest()
	if (pw_hash != true_pw_hash):
		# print ("Wrong password!")
		return (False)
	return (True)

def send_OTP (email):
	# Send OTP to mail
	s = smtplib.SMTP('mmtp.iitk.ac.in', 25)
	s.login('rohitkb', base64.b64decode('Vm9ydGV4MTIz').decode("utf-8"))
	# otp = str(np.random.randint(10000,100000))
	otp = '12345'
	s.sendmail('rohitkb@iitk.ac.in', email, otp)
	s.quit()
	return (otp)

if __name__ == '__main__':
	email = input("Enter e-mail: ")
	pw = getpass.getpass('Password: ')
	verify(email,pw)