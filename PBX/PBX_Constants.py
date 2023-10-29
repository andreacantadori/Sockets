# Desc: Constants for the PBX

# Number I/O ports for OETools and Workshops
# There are N_PORTS for each of the two types of ports
# i.e. N_PORTS for OETools and N_PORTS for Workshops
# It is useless to have more Workshop ports than OETool ports

N_PORTS = 4

# Base port numbers
# The actual port numbers will be BASE_PORT + i, where i = [0, N_PORTS-1]
BASE_WORKSHOP_PORT = 40000
BASE_OETOOL_PORT = 50000

# Port for the control socket
CONTROL_PORT = 45000

BASE_SOCKET_IP = '0.0.0.0' # Listen on all interfaces
