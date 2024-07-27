from heimdallr.all import *
from heimdallr.networking.network import *
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--local', help="Use localhost instead of intranet address.", action='store_true')
parser.add_argument('-d', '--detail', help="Show detailed log messages.", action='store_true')
args = parser.parse_args()

# Get desired IP address
if args.local:
	ip_address = "localhost"
else:
	ip_address = "192.168.1.116"

if __name__ == '__main__':
	
	# Create log object
	log = LogPile()
	log.str_format.show_detail = args.detail
	
	# Create client agent
	ca = HeimdallrClientAgent(log)
	ca.set_addr(ip_address, 5555)
	ca.connect_socket()
	
	# login to server with default admin password
	ca.login("admin", "password")
	ca.register_client_id("driver_main")
	
	# Create client options
	copt = ClientOptions()
	
	# Create a driver manager to handle the drivers
	dm = DriverManager(log, ca)
	
	# Create instrument driver and register with server
	scope1 = RigolDS1000Z("TCPIP0::192.168.1.20::INSTR", log, remote_id="Scope1", client_id=ca.client_id)
	
	# Add an instrument to DriverManager. This will register it with the server and 
	# add it to the DM's lookup table.
	dm.add_instrument(scope1)
	
	# Begin main loop s.t. this client executes the instructions from the server (which receives them from other clients)
	
	while True:
		
		# Listen for commands from server
		net_cmds = ca.dl_listen()
		
		# Check for error
		if net_cmds is None:
			log.error("An error occured while fetching NetworkCommands from the server.")
		
		for nc in net_cmds:
			
			if nc is None:
				log.warning("A 'None' snuck into the NetworkCommands list!")
				continue
			
			dm.route_command(nc)
		
		
	
	# # Begin listening mode
	# ca.begin_listener_mode()
	
	# # Run main function
	# ca.forward_commands([scope1])