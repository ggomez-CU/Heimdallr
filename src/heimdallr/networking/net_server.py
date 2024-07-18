from colorama import Fore, Style, Back

from pyfrost.pyfrost import *
from pyfrost.pf_server import *

from heimdallr.networking.network import *
from heimdallr.all import *

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dataclasses import dataclass

# TODO: Make this configurable and not present in most client copies
DATABASE_LOCATION = "userdata.db"

class ServerMaster:
	''' This class contains data shared between multiple clients. '''
	
	def __init__(self):
		
		# Initailize ThreadSafeData object to track instruments
		self.network_instruments = ThreadSafeData()
		self.network_instruments.add_list("instruments")
	
	def add_instrument(self, inst_id:Identifier) -> bool:
		''' Adds an instrument to the network. Returns boolean for success status.'''
		
		# Check if remote_id or remote_addr are already used in network_instruments
		if len(self.network_instruments.find_attr("instruments", "remote_id", inst_id.remote_id)) > 0:
			self.log.debug(f"Failed to add instrument because remote_id was already claimed on server.")
			return False
		if len(self.network_instruments.find_attr("instruments", "remote_addr", inst_id.remote_addr)) > 0:
			self.log.debug(f"Failed to add instrument because remote_addr was already claimed on server.")
			return False
		
		# Add to list
		self.network_instruments.list_append("instruments", inst_id)
		
		return True

serv_master = ServerMaster()

# class HeimdallrServerAgent:
	
# 	def __init__(self, **kwargs):
# 		super().__init__(**kwargs)
		
# 		# Look up instrument
# 		self.instrument_lookup = []

def server_callback_send(sa:ServerAgent, gc:GenCommand):
	''' Function passed to ServerAgents to execute custom send-commands for Heimdallr
	 networks (ie. those without a return value). '''
	global serv_master
	
	pass

def server_callback_query(sa:ServerAgent, gc:GenCommand):
	''' Function passed to ServerAgents to execute custom query-commands for Heimdallr
	 networks (ie. those with a return value). '''
	global serv_master
	
	gd_err = GenData({"STATUS": False})
	
	if gc.command == "REG-INST":
		
		# Check fields present
		if not gc.validate_reply(["REMOTE-ID", "REMOTE-ADDR"]):
			gd_err.metadata['error_str'] = "Failed to validate command."
			return gd_err
		
		# Find remote-id or remote-addr, whichever are populated.
		if len(gd_err.data['REMOTE-ID']) > 0:
			fidx = serv_master.find_attr("instruments", "remote_id", gd_err.data['REMOTE-ID'])
			
		else:
			fidx = serv_master.find_attr("instruments", "remote_address", gd_err.data['REMOTE-ADDR'])
		
		# Make sure an entry was found
		if len(fidx < 1):
			gd_err.metadata("Failed to find specified instrument registered on server.")
			return gd_err
		
		# Access database
		rid = serv_master.read_attr("instruments", fidx, "remote_id")
		radr = serv_master.read_attr("instruments", fidx, "remote_addr")
		
		# Populate GenData response
		gdata = GenData({"STATUS":True, "REMOTE-ID":rid, "REMOTE-ADDR": radr})
		return gdata
	
	pass