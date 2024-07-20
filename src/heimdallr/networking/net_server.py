from colorama import Fore, Style, Back

from pyfrost.base import *
from pyfrost.pf_server import *

from heimdallr.networking.network import *
from heimdallr.base import *

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
		self.master_data = ThreadSafeData()
		self.master_data.add_param("instruments")
	
	def add_instrument(self, inst_id:Identifier) -> bool:
		''' Adds an instrument to the network. Returns boolean for success status.'''
		
		# Acquire mutex
		with self.master_data.mtx:
		
			# Check if remote_id or remote_addr are already used in master_data
			if len(self.master_data.find_attr("instruments", "remote_id", inst_id.remote_id)) > 0:
				self.log.debug(f"Failed to add instrument because remote_id was already claimed on server.")
				return False
			if len(self.master_data.find_attr("instruments", "remote_addr", inst_id.remote_addr)) > 0:
				self.log.debug(f"Failed to add instrument because remote_addr was already claimed on server.")
				return False
		
			# Add to list
			self.master_data.append("instruments", inst_id)
		
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
	
	if gc.command == "REG-INST": # Register instrument
		
		# Check fields present
		if not gc.validate_command(["REMOTE-ID", "REMOTE-ADDR", "CTG", "IDN-MODEL", "DVR"], log):
			return False
		
		nid = Identifier()
		nid.remote_addr = gc.data['REMOTE-ADDR']
		nid.remote_id = gc.data['REMOTE-ID']
		nid.ctg = gc.data['CTG']
		nid.dvr = gc.data['DVR']
		nid.idn_model = gc.data['IDN-MODEL']
		
		# Add instrument to database
		serv_master.add_instrument(nid)
		
		return True
	
	# Return None if command is not recognized
	return None

def server_callback_query(sa:ServerAgent, gc:GenCommand):
	''' Function passed to ServerAgents to execute custom query-commands for Heimdallr
	 networks (ie. those with a return value). '''
	global serv_master
	
	gd_err = GenData({"STATUS": False})
	
	if gc.command == "LOC-INST": # Locate instrument
		
		# Check fields present
		if not gc.validate_command(["REMOTE-ID", "REMOTE-ADDR"], log):
			gd_err.metadata['error_str'] = "Failed to validate command."
			return gd_err
		
		# Acquire mutex
		with serv_master.master_data.mtx:
		
			# Find remote-id or remote-addr, whichever are populated.
			if (gc.data['REMOTE-ID'] is not None) and (len(gc.data['REMOTE-ID']) > 0):
				fidx = serv_master.master_data.find_attr("instruments", "remote_id", gc.data['REMOTE-ID'])
			else:
				fidx = serv_master.master_data.find_attr("instruments", "remote_address", gc.data['REMOTE-ADDR'])
			
			# Make sure an entry was found
			if len(fidx) < 1:
				gd_err.metadata['error_str'] = "Failed to find specified instrument registered on server."
				return gd_err
			
			# Convert from list to first hit (int)
			fidx = fidx[0]
			
			# Access database
			rid = serv_master.master_data.read_attr("instruments", fidx, "remote_id")
			radr = serv_master.master_data.read_attr("instruments", fidx, "remote_addr")
			rdvr = serv_master.master_data.read_attr("instruments", fidx, "dvr")
			rctg = serv_master.master_data.read_attr("instruments", fidx, "ctg")
			ridn = serv_master.master_data.read_attr("instruments", fidx, "idn_model")
		
		# Populate GenData response
		gdata = GenData({"STATUS":True, "REMOTE-ID":rid, "REMOTE-ADDR": radr, "CTG":rctg, "DVR":rdvr, "IDN-MODEL":ridn})
		return gdata
	
	if gc.command == "LIST-INST": # Return a list of all network-registered instruments
		
		#NOTE: Validation not performed because no additional parameters are expected
		
		# Initialize arrays
		rid = []
		radr = []
		rdvr = []
		rctg = []
		ridn = []
		
		# Hold master_data across multiple operations
		with serv_master.master_data.mtx:
		
			# Get length to iterate over
			param_len = serv_master.master_data.get_param_len("instruments")
			
			# Loop over length
			for fidx in range(param_len):
				
				# Access database
				rid.append(serv_master.master_data.read_attr("instruments", fidx, "remote_id"))
				radr.append(serv_master.master_data.read_attr("instruments", fidx, "remote_addr"))
				rdvr.append(serv_master.master_data.read_attr("instruments", fidx, "dvr"))
				rctg.append(serv_master.master_data.read_attr("instruments", fidx, "ctg"))
				ridn.append(serv_master.master_data.read_attr("instruments", fidx, "idn_model"))
		
		# Populate GenData response
		gdata = GenData({"STATUS":True, "REMOTE-ID":rid, "REMOTE-ADDR": radr, "CTG":rctg, "DVR":rdvr, "IDN-MODEL":ridn})
		return gdata
	
	# Return None if command is not recognized
	return None