"""RIGOL’s 1000Z Series Digital Oscilloscope
"""

from heimdallr.instrument_control.categories.all_ctgs import *

class LakeShoreModel335(PIDTemperatureControllerCtg):

	def __init__(self, address:str, log:LogFile):
		super().__init__(address, log)
	
	def set_setpoint(self, temp_K:float, channel:int=1):
		self.inst.write(f"SETP {channel},{temp_K}")
	def get_setpoint(self, temp_K:float, channel:int=1):
		self.inst.write(f"SETP? {channel}")
	
	def get_temp(self, temp_K:float, channel:int=1):
		self.inst.query(f"SETP? {channel}")
	
	def set_pid(self, P:float, I:float, D:float, channel:int=1):
		P = max(0.1, min(P, 1000))
		I = max(0.1, min(I, 1000))
		D = max(0.1, min(D, 1000))
		
		# Print a warning if any variable was adjusted
		if P != P or I != I or D != D:
			self.log.error(f"Did not apply command. Instrument limits values to 0.1-1000 and this range was violated.")
		
		self.write(f"PID {channel}")
	
	def get_pid(self, channel:int=1):
		
		pid_str = self.query(f"PID? {channel}")
		#TODO: Process string
		return None
	
	def set_range():
		pass
		#Will be RANGE command
	
	def set_enable(self, enable:bool, channel:int=1):
		pass
		#PRobably OUTMODE command, but should play around with this