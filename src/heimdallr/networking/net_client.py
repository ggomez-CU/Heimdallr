from pylogfile.base import *
from heimdallr.networking.network import *
from heimdallr.base import *

class HeimdallrClientAgent(ClientAgent):
	
	def __init__(self, log:LogPile, address:str=None, port:int=None, **kwargs):
		super().__init__(log=log, address=address, port=port, **kwargs)
		
		self.client_id = ""
	
	def register_instrument(self,id:Identifier, override:bool=False):
		''' Registers an instrument with the server so it can be found by other clients
		as a RemoteInstrument. This essentially just tells the server this instrument
		exists, and which incoming client to route instructions to. '''
		
		if len(self.client_id) == 0:
			self.log.warning("Cannot register instruments until the client has registered under a valid Client-ID.")
			return False
		
		#TODO: Allow admin to override, replacing any currently registered instruments with this one.
		
		# Tell server you wish to connect to this instrument
		gc = GenCommand("REG-INST", {"REMOTE-ID":id.remote_id, "REMOTE-ADDR":id.remote_addr, "IDN-MODEL":id.idn_model, "CTG":id.ctg, "DVR":id.dvr })
		
		# Send command to server and check for status
		if not self.send_command(gc):
			self.log.error("Failed to register instrument. Received fail from server.", detail=f"Tried to register remote_id={id.remote_id}, remote_address={id.remote_addr}")
			return False
		else:
			self.log.debug(f"Successfully registered instrument (remote_id={id.remote_id}, remote_address={id.remote_addr}).")
			
		return True
	
	def get_network_instrument_list(self, print_ids:bool=False):
		''' Gets a list of registered instruments from the server. Returns None if an error occurs, otherwise
		returns a list of the Identifiers'''
		
		# Prepare command
		gc = GenCommand("LIST-INST", {})
		
		data_packet = self.query_command(gc)
		
		# Check for missing packet
		if data_packet is None:
			self.connected = False
			return None
		
		# Check for error in packet
		if not data_packet.validate_reply(['REMOTE-ID', 'REMOTE-ADDR', 'CTG', 'DVR', 'IDN-MODEL'], self.log):
			self.connected = False
			return None
		
		# Update data
		l_remote_id = data_packet.data['REMOTE-ID']
		l_remote_addr = data_packet.data['REMOTE-ADDR']
		l_ctg = data_packet.data['CTG']
		l_dvr = data_packet.data['DVR']
		l_idn_model = data_packet.data['IDN-MODEL']
		
		# Check all have same length
		it = iter([l_remote_id, l_remote_addr, l_ctg, l_dvr, l_idn_model])
		num_inst = len(next(it))
		if not all(len(l) == num_inst for l in it):
			return None
		
		# Create list of Identifiers
		id_list = []
		for idx in range(num_inst):
			
			# Create new Identifier and populate
			nid = Identifier()
			nid.remote_id = l_remote_id[idx]
			nid.remote_addr = l_remote_addr[idx]
			nid.ctg = l_ctg[idx]
			nid.dvr = l_dvr[idx]
			nid.idn_model = l_idn_model[idx]
			
			# Add to list
			id_list.append(nid)
		
		# Print identifiers if asked
		table_data = []
		table_data.append(["remote-id", "remote-addr", "ctg", "dvr", "idn-model"])
		if print_ids:
			for id in id_list: # Print each identifier
				table_data.append([id.remote_id, id.remote_addr, id.ctg, id.dvr, id.idn_model])
			T = tabulate.tabulate(table_data, headers='firstrow', tablefmt='fancy_grid')
			print(str(T))
		
		self.connected = True
		
		return id_list
	
	def register_client_id(self, client_id:str, override:bool=False):
		''' Registers this client with a specific name on the server '''
		
		#TODO: Allow admin to override, replacing any previous clients with this name
		# with this one.
		
		# Prepare command
		gc = GenCommand("REG-CLIENT", {"ID":client_id})
		
		# Send command to server and check for status
		if not self.send_command(gc):
			self.log.error("Failed to register client-id. Received fail from server.", detail=f"Tried to register client-id={client_id}")
			return False
		else:
			self.log.debug(f"Successfully registered client as client-id={client_id}.")
		
		# Registration was successful - assign new ID
		self.client_id = client_id
		
		return True
	
	def dl_listen(self):
		'''(For Driver/Listener clients) Asks the server for any latent NetworkCommand 
		objects from Terminal/Command clients. The server will check repeatedly until a
		timeout occurs (set DL_LISTEN_TIMEOUT_OPTION and DL_LISTEN_CHECK_OPTION in
		server_master, both index zero). Will execute any latent commands.
		
		Returns None if error, else list of NetworkCommand objects to execute.
		'''
		
		# Prepare general command
		gc = GenCommand("DL-LISTEN", {})
		
		# Send command and get reply
		data_packet = self.query_command(gc)
		
		# Check for missing packet
		if data_packet is None:
			self.log.error(f"DL-LISTEN received no datapacket.")
			self.connected = False
			return None
		
		# Check for error in packet
		if not data_packet.validate_reply(['STATUS', 'NETCOMS'], self.log):
			self.log.error(f"DL-LISTEN received invalid GenData reply.")
			self.connected = False
			return None
		
		# Unpack all received netcoms
		netcoms = []
		for ncp in data_packet.data['NETCOMS']:
			
			print(f"NCP = {ncp}")
			
			# Create NC from unpacking string
			nc = NetworkCommand()
			nc.unpack(ncp)
			
			# Add to list
			netcoms.append(nc)
		
		print(f"netcoms = {netcoms}")
		
		return netcoms
	
class RemoteInstrument:
	''' Class to represent an instrument driven by another host on this network. This
	class allows remote clients to control the instrument, despite not having a 
	connection or driver locally.
	'''
	
	def __init__(self, ca:ClientAgent, log:LogPile, remote_id:str=None, remote_address:str=None):
		
		# Populate id
		self.id = Identifier()
		self.id.remote_id = remote_id
		self.id.remote_addr = remote_address
		
		self.log = log
		self.client_agent = ca
		
		self.connected = False # True if sucessfully connected to a remote instrument via server.
		
		# # Register with server - this will populate
		self.locate_instrument()
	
	def locate_instrument(self):
		''' Sends instrument identifier data to the server and locates the instrument
		on the network, linking the RemoteIntrument instance with that driver instance. '''
		#TODO: Verify that remote_id or remote_address are valid
		
		# Tell server you wish to connect to this instrument
		gc = GenCommand("LOC-INST", {"REMOTE-ID":self.id.remote_id, "REMOTE-ADDR":self.id.remote_addr })
		
		data_packet = self.client_agent.query_command(gc)
		
		# Check for missing packet
		if data_packet is None:
			self.connected = False
			return
		
		# Check for error in packet
		if not data_packet.validate_reply(['REMOTE-ID', 'REMOTE-ADDR', 'CTG', 'DVR', 'IDN-MODEL'], self.log):
			self.connected = False
			return
		
		# Update data
		self.id.remote_id = data_packet.data['REMOTE-ID']
		self.id.remote_addr = data_packet.data['REMOTE-ADDR']
		self.id.ctg = data_packet.data['CTG']
		self.id.dvr = data_packet.data['DVR']
		self.id.idn_model = data_packet.data['IDN-MODEL']
		self.connected = True
	
	def remote_call(self, func_name:str, *args, **kwargs):
		''' Calls the function 'func_name' of a remote instrument. Asynchronous, does
		 not wait for reply from server. '''
		
		arg_str = ""
		arg_dict = {}
		kwargs_dict = {}
		arg_idx = 0
		for a in args:
			arg_str = arg_str + f"{a} " # Make debug string
			arg_dict[arg_idx] = a # Make dictionary
			arg_idx += 1
		for key, value in kwargs.items():
			arg_str = arg_str + f"{key}:{value} " # Make debug string
			kwargs_dict[key] = value # Make dictionary
		
		# Enter debug log
		self.log.debug(f"Initializing remote call: function = {func_name}, arguments = {arg_str} ")
		
		# Create GC
		gc = GenCommand("REMCALL", {"REMOTE-ID":self.id.remote_id, "REMOTE-ADDR":self.id.remote_addr, "FUNCTION":func_name, "ARGS": arg_dict, "KWARGS": kwargs_dict})
		
		# Send command to server
		if not self.client_agent.send_command(gc):
			self.log.error("Remote call command failed. Received fail from server.")
			return False
		else:
			self.log.debug(f"Successfully sent remote call command to server.")
			
		return True
	
def RemoteFunction(func):
	'''Decorator to allow empty functions to call
	their remote counterparts'''
	
	def wrapper(self, *args, **kwargs):
		self.remote_call(func.__name__, *args, **kwargs)
		func(self, *args, **kwargs)
	return wrapper
