
class RemoteInstrument:
	''' Class to represent an instrument driven by another host on this network. This
	class allows remote clients to control the instrument, despite not having a 
	connection or driver locally.
	'''
	
	def __init__(self, ca:ClientAgent, remote_id:str=None, remote_address:str=None):
		
		# Save values
		self.remote_id = remote_id
		self.remote_address = remote_address
		self.client_agent = None
		
		# Register with server - this will populate
		self.register_instrument(remote_id=self.remote_id, remote_address=self.remote_address)
	
	def register_instrument(remote_id:str=None, remote_address:str=None):
		pass
	
		#TODO:  Ask server for instrument info
		
		#TODO: Update id and address
		# self.remote_id = 
		# self.remote_address = 
	
	def remote_call(self, func_name:str, *args, **kwargs):
		''' Calls the function 'func_name' of a remote instrument '''
		
		arg_str = ""
		for a in args:
			arg_str = arg_str + f"{a} "
		for key, value in kwargs.items():
			arg_str = arg_str + f"{key}:{value} "
		
		print(f"Initializing remote call: function = {func_name}, arguments = {arg_str} ")

def RemoteFunction(func):
	'''Decorator to allow empty functions to call
	their remote counterparts'''
	
	def wrapper(self, *args, **kwargs):
		self.remote_call(func.__name__, *args, **kwargs)
		func(self, *args, **kwargs)
	return wrapper
