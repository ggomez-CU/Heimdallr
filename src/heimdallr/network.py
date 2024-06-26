import socket
import rsa
import tabulate
import threading
import hashlib
import sqlite3
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pylogfile import *

ACCOUNT_ADMIN = 30
ACCOUNT_STANDARD = 20
ACCOUNT_LOW = 10

# Initialize database access
db_mutex = threading.Lock() # Create a mutex for the database

class UserDatabase:
	""" Handles interactions with, and manipulations of the user data database.
	
	It is supposed to abstract two things:
		1.) Hide database access from the coder using the 'db_mutex' variable
		2.) Hide SQL queries by burying them in functions
		3.) Hide database structure (in SQL queries) by burying it in functions.
		
	This way it's easy to restrucutre the database in the future if needed, and 
	there's no need to worry about database resource locks/races.
	"""
	
	def __init__(self, filename:str):
		
		# Name of database file
		self.filename = filename
		
	def remove_user(self, username:str):
		""" Deletes a user from the database """
		
		# Aquire mutex to protect database
		with db_mutex:
			
			conn = sqlite3.connect(self.filename)
			cur = conn.cursor()
			
			cur.execute("DELETE FROM userdata WHERE username = ?", (username,))
			
			conn.commit()
		
	def add_user(self, username:str, password:str, email:str, usr_type:str):
		""" Adds a user to the database """

		# Verify that user type is valid
		if usr_type not in [ACCOUNT_LOW, ACCOUNT_STANDARD, ACCOUNT_ADMIN]:
			usr_type = ACCOUNT_LOW
		
		# Get hash of password
		password_hash = hashlib.sha256(password.encode()).hexdigest()
		
		# Aquire mutex to protect database
		with db_mutex:
		
			conn = sqlite3.connect(self.filename)
			cur = conn.cursor()
						
			# Lookup highest account ID
			cur.execute("SELECT MAX(acct_id) FROM userdata")
			fd = cur.fetchall()
			try:
				next_ID = int(fd[0][0])+1
			except:
				self.log.critical(f"{self.id_str}Failed to access account ID from database.")
				return False
		
			cur.execute("INSERT INTO userdata (username, password, acct_id, email_addr, verified, acct_type) VALUES (?, ?, ?, ?, ?)", (username, password_hash, next_ID , email, "No", usr_type))
			conn.commit()
	
	def get_user_id(self, username:str):
		""" Accepts a username and looks up the ID of that user. Returns None if 
		user is not found in the database."""
		
		# Aquire mutex to protect database
		with db_mutex:
			
			conn = sqlite3.connect(self.filename)
			cur = conn.cursor()
			
			# Check for user
			cur.execute("SELECT id FROM userdata WHERE username = ?", (username,))
			qd = cur.fetchall()
			if qd:
				return qd[0][0]
			else:
				return None
	
	def get_user_type(self, username:str):
		""" Accepts a username and looks up the account type of that user. Returns None if
		user is not found in the database."""
		
		# Aquire mutex to protect database
		with db_mutex:
			
			conn = sqlite3.connect(self.filename)
			cur = conn.cursor()
			
			# Check for user
			cur.execute("SELECT acct_type FROM userdata WHERE username = ?", (username,))
			qd = cur.fetchall()
			if qd:
				return qd[0][0]
			else:
				return None

	def view_database(self):
		""" Access the entire database contents and return a table string"""
		
		# Hardcode - do not show password
		show_password = False
		
		# Query data from database
		with db_mutex:
			conn = sqlite3.connect(self.filename)
			cur = conn.cursor()
			
			cur.execute("SELECT * FROM userdata")
			
			# Get names
			names = list(map(lambda x: x[0], cur.description))
			
			# If told to hide password, deletes entry from names
			del_idx = None
			if not show_password:
				
				# Find password entry
				for idx, n in enumerate(names):
					if n == "password":
						del_idx = idx
				
				# Delete password item
				if del_idx is not None:
					del names[del_idx]
			
			# Get data
			cd = cur.fetchall()
		
		# Initialize master list
		table_data = []
		table_data.append(names)
		
		# Add user entries, one by one
		for entry in cd:
			
			# Create list
			entry_list = []
					
			# Scan over items in user entry
			for idx, e_item in enumerate(entry):
				
				# Skip passwords
				if idx == del_idx:
					continue
				
				entry_list.append(e_item)
		
			# Add to master lis
			table_data.append(entry_list)

		# Create table	
		T = tabulate.tabulate(table_data, headers='firstrow', tablefmt='fancy_grid')
		
		return str(T)

