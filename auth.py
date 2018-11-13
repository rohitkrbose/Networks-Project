import numpy as np
import hashlib
import getpass
import sqlite3
import smtplib 
import sys
import time

def verify (email,pw):
	connection = sqlite3.connect("back.db")
	cur = connection.cursor()

	# Check if exists
	comm = 'SELECT * FROM USER WHERE email=' + '\"' + email + '\"' 
	cur.execute(comm)
	res = cur.fetchall()
	if (len(res) == 0):
		print ('User does not exist!')
		return (False)
	true_pw_hash = res[0][1]

	# Check if password hashes match
	hash_obj = hashlib.md5(pw.encode('utf-8'))
	pw_hash = hash_obj.hexdigest()
	if (pw_hash != true_pw_hash):
		print ("Wrong password!")
		return (False)

	# Send OTP to mail
	s = smtplib.SMTP('mmtp.iitk.ac.in', 25)
	z = getpass.getpass('Rohit\'s Password: ')
	s.login('rohitkb', z)
	true_otp = str(np.random.randint(10000,100000))
	s.sendmail('rohitkb@iitk.ac.in', email, true_otp)
	s.quit()
	now = time.time()

	# Match OTPs
	otp = input('Enter OTP: ')
	if (otp == true_otp):
		print ("Authentication successful!")
	else:
		print ("Wrong OTP!")
		return (False)

	then = time.time()
	elapsed = then - now
	return (True)

if __name__ == '__main__':
	email = input("Enter e-mail: ")
	pw = getpass.getpass('Password: ')
	verify(email,pw)