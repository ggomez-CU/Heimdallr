from pyfrost.base import *
from pyfrost.pf_client import *
from heimdallr.base import *

class NetworkCommand(Packable):
	''' Object used to represent a function call passed over the Heimdallr
	network to a remote instrument. '''
	
	def __init__(self, gc:GenCommand=None):
		super().__init__()
		
		# Target client to process command
		self.target_client = ""
		
		# Target instrument to execute command
		self.remote_id = ""
		self.remote_addr = ""
		
		# Command data
		self.function = {}
		self.args = {}
		self.kwargs = {}
		
		# Source of command
		self.source_client = ""
		self.timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')) # From time object is created on server, not time it is sent from client.
		
		# Initialize from gc if provided
		if gc is not None:
			
			self.remote_id = gc.data['REMOTE-ID']
			self.remote_addr = gc.data['REMOTE-ADDR']
			
			self.function = gc.data['FUNCTION']
			self.args = gc.data['ARGS']
			self.kwargs = gc.data['KWARGS']
			
			try:
				pipe_idx = self.remote_addr.find("|")
				self.target_client = self.remote_addr[:pipe_idx]
			except Exception as e:
				print(f"Failed to get target-client from remote address.", detail=f"Error message: {e}") #TODO: This needs to be removed or a log
				self.target_client = ""
			
	def set_manifest(self):
		
		self.manifest.append("target_client")
		
		self.manifest.append("remote_id")
		self.manifest.append("remote_addr")
		
		self.manifest.append("function")
		self.manifest.append("args")
		self.manifest.append("kwargs")
		
		self.manifest.append("source_client")
		self.manifest.append("timestamp")

class DriverManager:
	''' Accepts a number of driver instances and allows them to be interacted with
	over a network.
	'''
	
	#TODO: Implement multi-threading
	
	def __init__(self, log:LogPile, ca:ClientAgent=None):
		
		self.drivers = {} # Dictionary mapping key=remote-addr to value=Driver-objects
		self.log = log
		
		# ClientAgent - if None, will ignore all network operations
		self.ca = ca 
	
	def route_command(self, command:NetworkCommand) -> bool:
		''' Executes a NetworkCommand by translating the relevant command into
		a function call for the target driver. Returns true false for succcess status.'''
		
		# Verify that target is in lookup table
		if not command.remote_addr in self.drivers:
			self.log.error(f"DriverManager unable to route NetworkCommand because requested remote-addr is not in lookup table.")
			return False
		
		# Translate NetworkCommand into a function call
		
		# Try to grab function handle
		try:
			# Try to get function handle from driver object
			func_handle = getattr(self.drivers[command.remote_addr], command.function)
		except AttributeError as e:
			self.log.error(f"DriverManager unable to route command because the specified driver does not have the requested function.", detail=f"driver remote address={command.remote_addr}, function={command.function}(), error message: ({e})")
			return False
		
		# Unpack args into list from dict
		#TODO: Iterate over this better (should be ints, but should double check all consecutive and starting ffrom  zero and in order. )
		args = []
		for k, v in command.args.items():
			args.append(v)
		
		# Try to call function
		try:
			rval = func_handle(*args, **command.kwargs)
		except TypeError as e:
			self.log.error(f"DriverManager unable to route command because the specified function did not accept the provided arguemnts.", detail=f"Error message: ({e})")
			return False
		
		
		#TODO: Do things with rval
	
	def add_instrument(self, instrument:Driver) -> bool:
		''' Adds an instrument to the DriverManager and will register it
		with the server if a ClientAgent was provided.
		
		Returns True if successfully added, else False.
		'''
		
		# Verify that instrument has a valid remote_addr
		if instrument.id.remote_addr == "":
			self.log.error(f"DriverManager cannot add an instrument without a populated remote-addr.")
			return False
		
		# Verify that instrument isn't already present
		if instrument.id.remote_addr in self.drivers:
			self.log.error(f"DriverManager cannot add an instrument whose remote-addr is already present in the driver list.")
			return False
		
		# Register instrument with server if possible
		if self.ca is not None:
			if not self.ca.register_instrument(instrument.id):
				self.log.error(f"DriverManager failed to register instrument with server.", detail=f"Instrument-ID: {instrument.id}")
			else:
				self.log.info(f"DriverManager successfully registered instrument with server.", detail=f"Instrument-ID: {instrument.id}")
		
		# Add to driver dictionary
		self.drivers[instrument.id.remote_addr] = instrument
		
		return True