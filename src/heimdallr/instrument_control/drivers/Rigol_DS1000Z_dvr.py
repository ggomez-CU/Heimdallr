"""RIGOL’s 1000Z Series Digital Oscilloscope
"""

from heimdallr.instrument_control.categories.all_ctgs import *

class RigolDS1000Z(OscilloscopeCtg):

	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log)
	
	def set_div_time(self, time_s:float):
		self.write(f":TIM:MAIN:SCAL {time_s}")
	def get_div_time(self):
		return self.query(f":TIM:MAIN:SCAL?")
	
	def set_offset_time(self, channel:int, time_s:float):
		self.write(f":TIM:MAIN:OFFS {time_s}")
	def get_offset_time(self, channel:int, time_s:float):
		return self.query(f":TIM:MAIN:OFFS?")
	
	def set_div_volt(self, channel:int, volt_V:float):
		self.write(f":CHAN{channel}:SCAL {volt_V}")
	def get_div_volt(self, channel:int, volt_V:float):
		return self.query(f":CHAN{channel}:SCAL?")
	
	def set_offset_volt(self, channel:int, volt_V:float):
		self.write(f":CHAN{channel}:OFFS {volt_V}")
	def get_offset_volt(self, channel:int, volt_V:float):
		return self.query(f":CHAN{channel}:OFFS?")
	
	def set_chan_enable(self, channel:int, enable:bool):
		self.write(f":CHAN{channel}:DISP {bool_to_str01(enable)}")
	def get_chan_enable(self, channel:int):
		val_str = self.query(f":CHAN{channel}:DISP?")
		return str01_to_bool(val_str)
	
	def get_waveform(self, channel:int):
		
		self.write(f"WAV:SOUR CHAN{channel}")  # Specify channel to read
		self.write("WAV:MODE NORM")  # Specify to read data displayed on screen
		self.write("WAV:FORM ASCII")  # Specify data format to ASCII
		data = self.query("WAV:DATA?")  # Request data
		
		if data is None:
			return {"time_s":[], "volt_V":[]}
		
		# Split string into ASCII voltage values
		volts = data[11:].split(",")
		
		volts = [float(v) for v in volts]
		
		# Get timing data
		xorigin = float(self.query("WAV:XOR?"))
		xincr = float(self.query("WAV:XINC?"))
		
		# Get time values
		t = list(xorigin + np.linspace(0, xincr * (len(volts) - 1), len(volts)))
		
		return {"time_s":t, "volt_V":volts}