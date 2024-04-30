from heimdallr.base import *

class PIDTemperatureControllerCtg(Driver):
	
	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log)
	
	def set_temp(self, temp_K:float, channel:int=1):
		pass
	
	def get_temp(self, temp_K:float, channel:int=1):
		pass
	
	def set_enable(self, enable:bool, channel:int=1):
		pass