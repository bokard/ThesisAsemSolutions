import socket

# IP address and port of the MXA920 microphone
ip_address = '192.168.1.61'
port = 2202

def establish_connection():
    """Establishes a TCP connection to the microphone."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_address, port))
    return sock

def set_position_reporting_rate(sock, rate):
    """Sets the talker position reporting rate."""
    command = f'< SET TALKER_POSITION_RATE {rate} >\r\n'
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print("Response:", response)

def process_talker_positions(data):
    """Processes the received talker positions."""
    positions = data.strip().split()[3:]
    num_positions = len(positions) // 7
    for i in range(num_positions):
        position = positions[i * 7: (i + 1) * 7]
        lobe_id, area_id, x, y, z = position[0:5]
        x, y, z = int(x), int(y), int(z)
        print("Talker", i + 1, "is at (X, Y, Z) =", (x, y, z),
              "which is covered by lobe", lobe_id, "in coverage area", area_id)

def listen_for_talker_positions(sock):
    """Listens for incoming talker positions continuously."""
    while True:
        data = sock.recv(1024).decode()
        
        # Check if the received data is a talker position report
        if data.startswith('< SAMPLE TALKER_POSITIONS'):
            process_talker_positions(data)

# Main program
sock = establish_connection()
set_position_reporting_rate(sock, 100)  # Set reporting rate to 100 ms
listen_for_talker_positions(sock)
