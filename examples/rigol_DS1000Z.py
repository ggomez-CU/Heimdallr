from heimdallr.all import *

log = LogFile()

osc = RigolDS1000Z("TCPIP0::192.168.2.11::INSTR", log)

