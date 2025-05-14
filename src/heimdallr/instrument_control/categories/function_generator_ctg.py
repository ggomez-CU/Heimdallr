from heimdallr.base import *

class FunctionGeneratorCtg0(Driver):
	
	def __init__(self, address:str, log:LogPile, expected_idn="", is_scpi:bool=False):
		super().__init__(address, log, expected_idn=expected_idn, is_scpi=is_scpi)
    

class FunctionGeneratorCtg1(FunctionGeneratorCtg0):
	
{SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER}

	# TODO: Flesh out
	MEAS_WAVEFORM_SIN = "SIN"
	MEAS_WAVEFORM_SQUARE = "SQU"
	MEAS_WAVEFORM_RAMP = "RAMP"
	MEAS_WAVEFORM_PULSE = "PULS"
	
	# TODO: Flesh out
	RANGE_AUTO = "auto-range"
	
	def __init__(self, address:str, log:LogPile, expected_idn=""):
		super().__init__(address, log, expected_idn=expected_idn)