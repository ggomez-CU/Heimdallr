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

instrument_lookup = ThreadSafeData()
instrument_lookup.add_list("instruments") # List of Identifier() objects
instrument_lookup.list_append("instruments", inst)
instrument_lookup.list_read("instruments", idx=0)
instrument_lookup.list_read_attr("instruments", idx=0, attr="remote_id")
instrument_lookup.list_set("instruments", idx=0, val=inst)
instrument_lookup.list_set_attr("instruments", idx=0, attr="remote_id", val="Oscilloscope-Rigol-Main")

class HeimdallrServerAgent:
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		# Look up instrument
		self.instrument_lookup = []

def server_callback_send(sa:ServerAgent, gc:GenCommand):
	'''  '''
	pass

def server_callback_query(sa:ServerAgent, gc:GenCommand):
	'''  '''
	pass