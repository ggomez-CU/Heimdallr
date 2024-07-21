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
	
	def __init__(self, master_log:LogPile):
		
		#TODO: Add way of printing status of each of these (ie. lengths of the lists)
		
		# Initailize ThreadSafeDict object to track instruments
		self.master_instruments = ThreadSafeList() # (type = Identifier)
		self.master_net_cmd = ThreadSafeList() # Contains objects describing commands to route to driver/listener clients (Type = NetworkCommand)
		self.master_net_reply = ThreadSafeList() # Contains objects describing response data to route to terminal/command clients (Type = GenData?)
		self.master_client_ids = ThreadSafeList() # Contains a list of all client-ids currently present on the server (type = string)
		
		self.log = master_log
	
	def add_instrument(self, inst_id:Identifier) -> bool:
		''' Adds an instrument to the network. Returns boolean for success status.'''
		
		# Acquire mutex
		with self.master_instruments.mtx:
		
			# Check if remote_id or remote_addr are already used in master_instruments
			if len(self.master_instruments.find_attr("remote_id", inst_id.remote_id)) > 0:
				self.log.debug(f"Failed to add instrument because remote_id was already claimed on server.")
				return False
			if len(self.master_instruments.find_attr("remote_addr", inst_id.remote_addr)) > 0:
				self.log.debug(f"Failed to add instrument because remote_addr was already claimed on server.")
				return False
		
			# Add to list
			self.master_instruments.append(inst_id)
		
		return True

master_log = LogPile()
serv_master = ServerMaster(master_log)

# Define parameters that go in sa.app_data (defined so harder to mistype)
CLIENT_ID = 'client_id'

def server_init_function(sa:ServerAgent):
	''' Initializes the server agent option with any preferences for the end application.
	Here it's just used to add feilds to the sa.app_data dict. Must return the modified
	sa. '''
	
	sa.app_data[CLIENT_ID] = ""
	return sa

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
	
	elif gc.command == "REG-CLIENT":
		
		# Check fields present
		if not gc.validate_command(["ID"], log):
			return False
		
		# Look for client already existing with this name
		with serv_master.master_client_ids.mtx:
			
			fidx = serv_master.master_client_ids.find(gc.data['ID'])
			if len(fidx) > 0: # client ID was found!
				return False
			
			# Add to list
			serv_master.master_client_ids.append(gc.data['ID'])
		
		# Save client-id to ServerAgent app_data
		sa.app_data[CLIENT_ID] = gc.data['ID']
		
		ncid = gc.data['ID']
		sa.log.debug(f"Registered client-id {ncid}")
		
		return True
	
	elif gc.command == "REMCALL":
		
		# Check fields present
		if not gc.validate_command(["REMOTE-ID", "REMOTE-ADDR", "FUNCTION", "ARGS", "KWARGS"], log):
			return False
		
		# Create a NetworkCommand object
		nc = NetworkCommand(gc=gc)
		
		# Add to master net command
		with serv_master.master_net_cmd.mtx:
			serv_master.master_net_cmd.append(nc)
		
		#TODO: Populate source_client in NetworkCommand object
		
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
		with serv_master.master_instruments.mtx:
		
			# Find remote-id or remote-addr, whichever are populated.
			if (gc.data['REMOTE-ID'] is not None) and (len(gc.data['REMOTE-ID']) > 0):
				fidx = serv_master.master_instruments.find_attr("remote_id", gc.data['REMOTE-ID'])
			else:
				fidx = serv_master.master_instruments.find_attr("remote_address", gc.data['REMOTE-ADDR'])
			
			# Make sure an entry was found
			if len(fidx) < 1:
				gd_err.metadata['error_str'] = "Failed to find specified instrument registered on server."
				return gd_err
			
			# Convert from list to first hit (int)
			fidx = fidx[0]
			
			# Access database
			rid = serv_master.master_instruments.read_attr(fidx, "remote_id")
			radr = serv_master.master_instruments.read_attr(fidx, "remote_addr")
			rdvr = serv_master.master_instruments.read_attr(fidx, "dvr")
			rctg = serv_master.master_instruments.read_attr(fidx, "ctg")
			ridn = serv_master.master_instruments.read_attr(fidx, "idn_model")
		
		# Populate GenData response
		gdata = GenData({"STATUS":True, "REMOTE-ID":rid, "REMOTE-ADDR": radr, "CTG":rctg, "DVR":rdvr, "IDN-MODEL":ridn})
		return gdata
	
	elif gc.command == "LIST-INST": # Return a list of all network-registered instruments
		
		#NOTE: Validation not performed because no additional parameters are expected
		
		# Initialize arrays
		rid = []
		radr = []
		rdvr = []
		rctg = []
		ridn = []
		
		# Hold master_instruments across multiple operations
		with serv_master.master_instruments.mtx:
		
			# Get length to iterate over
			param_len = serv_master.master_instruments.len()
			
			# Loop over length
			for fidx in range(param_len):
				
				# Access database
				rid.append(serv_master.master_instruments.read_attr(fidx, "remote_id"))
				radr.append(serv_master.master_instruments.read_attr(fidx, "remote_addr"))
				rdvr.append(serv_master.master_instruments.read_attr(fidx, "dvr"))
				rctg.append(serv_master.master_instruments.read_attr(fidx, "ctg"))
				ridn.append(serv_master.master_instruments.read_attr(fidx, "idn_model"))
		
		# Populate GenData response
		gdata = GenData({"STATUS":True, "REMOTE-ID":rid, "REMOTE-ADDR": radr, "CTG":rctg, "DVR":rdvr, "IDN-MODEL":ridn})
		return gdata
	
	elif gc.command == "DL-LISTEN": # Driver/Listener client is listening for new commands from server
		
		#NOTE: Validation not performed because no additional parameters are expected
		
		# Look for NetworkCommand objects assigned to this client
		
		# Prepare a GenData object with all NetworkCommand objects included
		
		return gdata
		
	# Return None if command is not recognized
	return None