""" Keysight 8360L Series Swept CW Generator
"""

from heimdallr.base import *
from heimdallr.instrument_control.categories.function_generator_ctg import *

class Keysight33120A(FunctionGeneratorCtg):

	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log, expected_idn="")
		
	
	def set_waveform(self, p_dBm:float):
		self.write(f"FUNCtion {SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER}")
	
	def set_freq(self, f_Hz:float):
		self.inst.write(f"FREQ{f_Hz}")
	def get_freq(self):
		return float(self.inst.query(f"FREQ?"))

    def set_volt(self, v_mag:float, v_dc:float=0):
		self.write(f"VOLT {v_mag}")
        self.write(f"VOLT:OFFS {v_dc}")


    def set_measurement(self, measurement:str, meas_range:str=DigitalMultimeterCtg1.RANGE_AUTO):
		''' Sets the measurement, using a DitigalMultimeterCtg0 constant. 
		Returns True if successful, else false.
		'''
		
		# Get measurement string
		match measurement:
			case DigitalMultimeterCtg1.MEAS_WAVEFORM_SIN:
				mstr = "RES" 
			case DigitalMultimeterCtg1.MEAS_WAVEFORM_SQUARE:
				mstr = "SQU"
			case DigitalMultimeterCtg1.MEAS_WAVEFORM_RAMP:
				mstr = "RAMP" 
			case DigitalMultimeterCtg1.MEAS_WAVEFORM_PULSE:
				mstr = "PULS"
			case _:
				self.log.error(f"Failed to interpret measurement argument '{measurement}'. Aborting.")
				return False
		
		self.write(f"FUNC {mstr}")
		
		return True