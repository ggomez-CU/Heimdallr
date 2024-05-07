from heimdallr.base import *

class RFPowerSensor(Driver):
	
	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log)