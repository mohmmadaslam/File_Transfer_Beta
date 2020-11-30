import threading
from server import Server
from multiprocessing import Process

# Download       -   instruction1
# Upload         -   instruction2
# Remove         -   instruction3
# Rename         -	instruction4
# Move           -	instruction5
# Back           -
# Forward		-
# Access_Folder  -
# file list      -   instruction6
# Search			-	instruction7

Port_number = 4444


def start_responding(server, Client_socket, Client_address):

	print(f"Started Responding to {Client_address[0]}: {Client_address[1]}")

	while True:
		current_directory = "./Local_server_files"
		print(f"Current Directory: {current_directory}")

		instruction = Client_socket.recv(server.instruction_length).decode('utf-8').strip()

		print(f"{instruction} As Instruction received")

		if instruction == "Instruction1":
			server.send_requested_file(Client_socket)

		elif instruction == "Instruction2":

			server.receive_file(Client_socket)

		elif instruction == "Instruction3":
			
			server.remove_file(Client_socket)

		elif instruction == "Instruction4":

			server.rename_file(Client_socket)

		# elif instruction == "Instruction5":	
		elif instruction == "Instruction6":
			
			server.send_file_list(Client_socket)

		elif instruction == "Instruction7":
		
			server.return_search(Client_socket)


server = Server(Port_number)
server.start_server()

while True:

	try:
		print("trying to connect to clients")
		Client_socket, Client_address = server.server_socket.accept()
		print(f"Connection has been established with IP: {Client_address[0]} PORT: {Client_address[1]}")
		threading._start_new_thread(start_responding, (server, Client_socket, Client_address))

	except KeyboardInterrupt as e:
		print(f"Gradually shutting down the server")

	except Exception as e:
		print(f"did not expected {e}!")