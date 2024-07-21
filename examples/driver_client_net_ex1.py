from heimdallr.all import *
from heimdallr.networking.network import *
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--local', help="Use localhost instead of intranet address.", action='store_true')
args = parser.parse_args()

# Get desired IP address
if args.local:
	ip_address = "localhost"
else:
	ip_address = "192.168.1.116"

if __name__ == '__main__':
	
	# Create log object
	log = LogPile()
	
	# Create client agent
	ca = HeimdallrClientAgent(log)
	ca.set_addr(ip_address, 5555)
	ca.connect_socket()
	
	# login to server with default admin password
	ca.login("admin", "password")
	ca.register_client_id("driver_main")
	
	# Create client options
	copt = ClientOptions()
	
	# Create remote instrument and register with server
	scope1 = RigolDS1000Z("TCPIP0::192.168.1.20::INSTR", log, remote_id="Scope1", client_id=ca.client_id)
	ca.register_instrument(scope1.id)
	
	# Begin main loop s.t. this client executes the instructions from the server (which receives them from other clients)
	
	while True:
		
		time.sleep(1)
		# ca.listen_command()
	
	# # Begin listening mode
	# ca.begin_listener_mode()
	
	# # Run main function
	# ca.forward_commands([scope1])