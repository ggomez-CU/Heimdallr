from heimdallr.all import *

# Create remote instruments from address
scope1 = OscilloscopeCtg2(remote_inst_address="192.168.0.14/GPIB::14")
scope2 = OscilloscopeCtg2(remote_inst_address="192.168.0.14/192.168.0.200")

# Create remote instruments from name
scope3 = OscilloscopeCtg2(remote_inst_name="Ibias_Oscilloscope")

scope3.set_chan_enable(2, False)

