from pylogfile.base import *
from heimdallr.networking.network import *
from heimdallr.base import *

class DriverClientAgent(ClientAgent):
	
	def __init__(self, log:LogPile, address:str=None, port:int=None, **kwargs):
		super().__init__(log=log, address=address, port=port, **kwargs)
	
	def register_instrument(self,id:Identifier):
		''' Registers an instrument with the server so it can be found by other clients
		as a RemoteInstrument. This essentially just tells the server this instrument
		exists, and which incoming client to route instructions to. '''
		
		# Tell server you wish to connect to this instrument
		gc = GenCommand("REG-INST", {"REMOTE-ID":id.remote_id, "REMOTE-ADDR":id.remote_addr, "IDN-MODEL":id.idn_model, "CTG":id.ctg, "DVR":id.dvr })
		
		# Send command to server and check for status
		if not self.send_command(gc):
			self.log.error("Failed to register instrument. Received fail from server.", detail=f"Tried to register remote_id={id.remote_id}, remote_address={id.remote_addr}")
			return False
		else:
			self.log.debug(f"Successfully registered instrument (remote_id={id.remote_id}, remote_address={id.remote_addr}).")
			
		return True
	
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
		''' Calls the function 'func_name' of a remote instrument '''
		
		arg_str = ""
		for a in args:
			arg_str = arg_str + f"{a} "
		for key, value in kwargs.items():
			arg_str = arg_str + f"{key}:{value} "
		
		print(f"Initializing remote call: function = {func_name}, arguments = {arg_str} ")
		
		#TODO: Send command to server
	
def RemoteFunction(func):
	'''Decorator to allow empty functions to call
	their remote counterparts'''
	
	def wrapper(self, *args, **kwargs):
		self.remote_call(func.__name__, *args, **kwargs)
		func(self, *args, **kwargs)
	return wrapper
