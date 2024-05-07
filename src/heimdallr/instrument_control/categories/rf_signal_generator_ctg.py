from heimdallr.base import *

class RFSignalGeneratorCtg(Driver):
	
	def __init__(self, address:str, log:LogPile, expected_idn:str=""):
		super().__init__(address, log, expected_idn=expected_idn)
	
	def set_power(self, p_dBm:float):
		pass
	
	def set_freq(self, f_Hz:float):
		pass
	
	def set_enable_rf(self,enable:bool):
		pass