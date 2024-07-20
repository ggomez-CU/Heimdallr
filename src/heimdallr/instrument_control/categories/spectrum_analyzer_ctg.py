from heimdallr.base import *
from heimdallr.networking.net_client import *

class SpectrumAnalyzerCtg(Driver):
	
	SWEEP_CONTINUOUS = "sweep-continuous"
	SWEEP_SINGLE = "sweep-single"
	SWEEP_OFF = "sweep-off"
	
	def __init__(self, address:str, log:LogPile, expected_idn:str=""):
		super().__init__(address, log, expected_idn=expected_idn)
	
	def set_freq_start(self, f_Hz:float, channel:int=1):
		pass
	
	def set_freq_end(self, f_Hz:float, channel:int=1):
		pass
	
	def set_num_points(self, points:int, channel:int=1):
		pass
	
	def set_res_bandwidth(self, rbw_Hz:float, channel:int=1):
		pass
	
	def clear_traces(self):
		pass
	
	def add_trace(self, channel:int, measurement:str):
		''' Returns trace number '''
		pass
	
	def get_waveform(self, channel:int):
		pass

#TODO: Make one of these for all instruments
#TODO: Flesh out
class SpectrumAnalyzerRemote(RemoteInstrument):
	
	def __init__(self):
		super().__init__()
	
	# Without the decorator, it looks like this
	def set_freq_start(self, f_Hz:float, channel:int=1):
		self.remote_call('set_freq_start', f_Hz, channel)
	
	# With the decorator, it looks like this
	@RemoteFunction
	def set_freq_end(self, f_Hz:float, channel:int=1):
		pass