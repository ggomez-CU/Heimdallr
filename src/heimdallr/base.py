import pyvisa as pv
from pylogfile import *
import numpy as np

class Identifier:
	
	def __init__(self):
		self.idn_model = "" # Identifier provided by instrument itself (*IDN?)
		self.ctg = "" # Category class of driver
		self.dvr = "" # Driver class
		self.name = "" # Rich name provided by user (optional)

class Driver:
	
	def __init__(self, address:str, log:LogPile, expected_idn:str=""):
		
		self.address = address
		self.log = log
		
		self.id = Identifier()
		self.expected_idn = expected_idn 
		self.verified_hardware = False
		
		self.online = False
		self.rm = pv.ResourceManager()
		self.isnt = None
		self.connect()
	
	def connect(self, check_id:bool=True):
		
		try:
			self.inst = self.rm.open_resource(self.address)
			self.online = True
			
			if check_id:
				self.query_id()
			
		except Exception as e:
			self.log.error(f"Failed to connect to address: {self.address}. ({e})")
			self.online = False
	
	def query_id(self):
		''' Checks the IDN of the instrument, and makes sure it matches up.'''
		
		# Query IDN model
		self.id.idn_model = self.query("*IDN?")
		
		if self.id.idn_model is not None:
			self.online = True
			self.log.debug(f"Instrument connection state: >ONLINE<")
			
			if self.expected_idn is None or self.expected_idn == "":
				self.log.debug("Cannot verify hardware. No verification string provided.")
				return
			
			# Check if model is right
			if self.expected_idn in self.id.idn_model:
				self.verified_hardware = True
				self.log.debug(f"Hardware verification >PASSED<", detail=f"Received string: {self.id.idn_model}")
			else:
				self.verified_hardware = False
				self.log.debug(f"Hardware verification >FAILED<", detail=f"Received string: {self.id.idn_model}")
		else:
			self.log.debug(f"Instrument connection state: >OFFLINE<")
			self.online = False
		
	def close(self):
		
		self.inst.close()
	
	def write(self, cmd:str):
		''' Sends a SCPI command via PyVISA'''
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
		
		try:
			self.inst.write(cmd)
		except Exception as e:
			self.log.error(f"Failed to write to instrument {self.address}. ({e})")
			self.online = False
		
	def id_str(self):
		pass
	
	def read(self):
		''' Reads via PyVISA'''
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
		
		try:
			return self.inst.write()
		except Exception as e:
			self.log.error(f"Failed to read from instrument {self.address}. ({e})")
			self.online = False
			return None
	
	def query(self, cmd:str):
		''' Querys a command via PyVISA'''
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
		
		try:
			return self.inst.query(cmd)
		except Exception as e:
			self.log.error(f"Failed to query instrument {self.address}. ({e})")
			self.online = False
			return None

def bool_to_str01(val:bool):
	''' Converts a boolean value to 0/1 as a string '''
	
	if val:
		return "1"
	else:
		return "0"

def str01_to_bool(val:str):
	''' Converts the string 0/1 to a boolean '''
	
	if '1' in val:
		return True
	else:
		return False

def bool_to_ONFOFF(val:bool):
	''' Converts a boolean value to 0/1 as a string '''
	
	if val:
		return "ON"
	else:
		return "OFF"

def str_to_bool(val:str):
	''' Converts the string 0/1 or ON/OFF or TRUE/FALSE to a boolean '''
	
	if ('1' in val) or ('ON' in val.upper()) or ('TRUE' in val.upper()):
		return True
	else:
		return False