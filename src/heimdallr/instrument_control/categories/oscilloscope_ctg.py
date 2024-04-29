from heimdallr.base import *

class OscilloscopeCtg(Driver):
	
	def __init__(self, address:str, log:LogFile):
		super().__init__(address, log)
	
	def set_div_time(self, time_s:float):
		pass
	
	def get_div_time(self, channel:int):
		pass
	
	def set_offset_time(self, channel:int, time_s:float):
		pass
	
	def set_div_volt(self, channel:int, volt_V:float):
		pass
	
	def set_offset_volt(self, channel:int, volt_V:float):
		pass
	
	def set_chan_enable(self, channel:int, enable:bool):
		pass
	
	def get_waveform(self, channel:int):
		pass