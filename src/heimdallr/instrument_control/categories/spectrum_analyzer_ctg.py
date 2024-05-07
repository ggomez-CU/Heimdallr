from heimdallr.base import *

class SpectrumAnalyzerCtg(Driver):
	
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