import threading
import socket

# Global variables
send_coordinates = False  # Flag to control sending of coordinates
coordinates = [0, 0, 0]  # XYZ coordinates

# Function to handle reading XYZ coordinates from the Shure MX920 microphone
def read_coordinates():
    global coordinates
    # Your code to read XYZ coordinates from the Shure MX920 microphone goes here
    # You can update the coordinates variable with the latest values
    
    # Dummy implementation (replace with actual implementation)
    coordinates = [1, 2, 3]  # Update coordinates with dummy values

    # Schedule the next reading after a certain interval
    threading.Timer(1.0, read_coordinates).start()

# Function to handle sending XYZ coordinates to the Bitfocus Companion program
def send_coordinates_to_companion():
    global send_coordinates
    global coordinates
    while True:
        if send_coordinates:
            # Your code to send XYZ coordinates to the Bitfocus Companion program goes here
            # You can use the coordinates variable to get the latest values
            
            # Dummy implementation (replace with actual implementation)
            print("Sending coordinates:", coordinates)  # Print coordinates to console
            
        # Sleep for a short interval before sending the next coordinates
        # Adjust the interval as per your requirements
        time.sleep(0.1)

# Function to handle the connection for enabling/disabling the sending of coordinates
def enable_disable_sender():
    global send_coordinates
    enable_disable_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    enable_disable_socket.bind(('localhost', 5000))  # Adjust the host and port as needed
    enable_disable_socket.listen(1)
    
    while True:
        conn, addr = enable_disable_socket.accept()
        data = conn.recv(1024).decode().strip().lower()
        
        if data == 'enable':
            send_coordinates = True
            conn.sendall(b'Sending of coordinates enabled')
        elif data == 'disable':
            send_coordinates = False
            conn.sendall(b'Sending of coordinates disabled')
        else:
            conn.sendall(b'Invalid command')
        
        conn.close()

# Create and start the threads
read_coordinates_thread = threading.Thread(target=read_coordinates)
send_coordinates_thread = threading.Thread(target=send_coordinates_to_companion)
enable_disable_thread = threading.Thread(target=enable_disable_sender)

read_coordinates_thread.start()
send_coordinates_thread.start()
enable_disable_thread.start()
