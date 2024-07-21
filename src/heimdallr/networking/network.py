from pyfrost.base import *
from pyfrost.pf_client import *

class NetworkCommand(Packable):
	''' Object used to represent a function call passed over the Heimdallr
	network to a remote instrument. '''
	
	def __init__(self, gc:GenCommand=None):
		
		# Target to execute command
		self.remote_id = ""
		self.remote_addr = ""
		
		# Command data
		self.function = {}
		self.args = {}
		self.kwargs = {}
		
		# Source of command
		self.source_client = None
		self.timestamp = None
		
		# Initialize from gc if provided
		if gc is not None:
			self.remote_id = gc.data['REMOTE-ID']
			self.remote_addr = gc.data['REMOTE-ADDR']
			
			self.function = gc.data['FUNCTION']
			self.args = gc.data['ARGS']
			self.kwargs = gc.data['KWARGS']
	
	def set_manifest(self):
		
		self.manifest.append("remote_id")
		self.manifest.append("remote_addr")
		
		self.manifest.append("function")
		self.manifest.append("args")
		self.manifest.append("kwargs")
		
		self.manifest.append("source_client")
		self.manifest.append("timestamp")
	