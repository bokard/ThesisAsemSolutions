import socket
import threading
import time
from collections import Counter

# IP addresses and ports
microphone_ip = '192.168.1.61'
microphone_port = 2202

companion_ip = '192.168.1.24'
companion_port = 16759
control_ip = '192.168.1.24'
control_port = 16780

# Shared variables for communication control
send_data = False
send_data_lock = threading.Lock()

# Extra shared settings
rate = "100"  # Time for the sampling rate of the Microphone (between 100 and 9999ms)
filter_window = 3  # Time for the rolling average filter in seconds
min_occurrences = 2  # Minimum number of occurrences for an area to be considered dominant

def establish_microphone_connection():
    """Establishes a TCP connection to the microphone."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((microphone_ip, microphone_port))
    return sock

def establish_companion_connection():
    """Establishes a TCP connection to the companion device."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((companion_ip, companion_port))
    return sock

def establish_control_connection():
    """Establishes a TCP connection for control signals."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((control_ip, control_port))
    sock.listen(1)
    conn, _ = sock.accept()
    return sock, conn

def set_position_reporting_rate(sock, rate):
    """Sets the talker position reporting rate."""
    command = f'< SET TALKER_POSITION_RATE {rate} >\r\n'
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print("Response:", response)

def process_talker_positions(data, companion_sock):
    """Processes the received talker positions."""
    positions = data.strip().split()[3:]
    num_positions = len(positions) // 7

    current_time = time.time()
    active_areas = []
    
def process_talker_positions(data, companion_sock):
    """Processes the received talker positions."""
    positions = data.strip().split()[3:]
    num_positions = len(positions) // 7

    current_time = time.time()
    active_areas = []
    try:
        for i in range(num_positions):
            position = positions[i * 7: (i + 1) * 7]
            lobe_id, area_id, x, y, z = position[0:5]
            x, y, z = int(x), int(y), int(z)
            message = f"Talker {i + 1}: X={x}, Y={y}, Z={z}, Lobe={lobe_id}, Area={area_id}"
            print(message)

            active_area = (area_id, current_time)
            # Add active area to rolling average list
            active_areas.append(active_area)

        if any(active_areas):
            # Remove areas older than the filter window
            active_areas = [area for area in active_areas if current_time - area[1] <= filter_window]

            # Count the occurrences of each active area
            count = Counter(tuple(area) for area in active_areas)

            # Get the most common active area
            dominant_area = count.most_common(1)[0]

            # Check if the dominant area occurs more than the minimum occurrences threshold
            if dominant_area[1] >= min_occurrences:
                active_area = dominant_area[0]
                print("Dominant active area:", active_area[0])
                send_data_to_companion(companion_sock, active_area[0])
            else:
                print("No dominant active area found.")

    except ValueError:
        print(data)

    
def send_data_to_companion(companion_sock, active_area):
    """Sends the talker position data to the companion device."""
    if send_data:
        data = "CUSTOM-VARIABLE active SET-VALUE " + active_area + "\r\n"
        companion_sock.sendall(data.encode())
        print("Data send:", data)

def listen_for_talker_positions(microphone_sock):
    """Listens for incoming talker positions continuously."""
    companion_sock = establish_companion_connection()
    while True:
        data = microphone_sock.recv(1024).decode()

        # Check if the received data is a talker position report
        if data.startswith('< SAMPLE TALKER_POSITIONS'):
            process_talker_positions(data, companion_sock)
            
def listen_for_control_signals(control_conn):
    """Listens for control signals to enable/disable data transmission."""
    global send_data
    while True:
        signal = control_conn.recv(1024).decode().strip()

        if signal == 'ENABLE':
            send_data_lock.acquire()
            send_data = True
            send_data_lock.release()
            print("Data transmission enabled.")

        elif signal == 'DISABLE':
            send_data_lock.acquire()
            send_data = False
            send_data_lock.release()
            print("Data transmission disabled.")
        
#Main program
microphone_sock = establish_microphone_connection()
set_position_reporting_rate(microphone_sock, rate)
companion_sock = establish_companion_connection()
control_sock, control_conn = establish_control_connection()

#Start separate threads for listening to talker positions, control signals, sending data to the companion device.
talker_position_thread = threading.Thread(target=listen_for_talker_positions, args=(microphone_sock,))
control_thread = threading.Thread(target=listen_for_control_signals, args=(control_conn,))

#Start the threads
talker_position_thread.start()
control_thread.start()