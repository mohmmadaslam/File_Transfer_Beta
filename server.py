import socket
import os
import pickle
import time
import re

from constants import PORT_, HEADER_LENGTH_, MAX_CONNECTION_, INSTRUCTION_LENGTH_, BUFFER_, PORT_RANGE_ 

class Server:

	def __init__(self, port=PORT_):
		if not os.path.exists("IpDetails.txt"):
			os.system("ipconfig >> IpDetails.txt")
		with open("IpDetails.txt") as f:
			text = f.read()
			if text.find("Ethernet adapter Ethernet:") != -1:
				self.HOST_ADDRESS = text.split("Ethernet adapter Ethernet:")[1].split("\n")[4].split(":")[1].strip()
			elif text.find("Wireless LAN adapter Wi-Fi:") != -1:
				print("No Ethernet found!")
				print("Hosting over Wi-Fi")
				self.HOST_ADDRESS = text.split("Wireless LAN adapter Wi-Fi:")[1].split("\n")[4].split(":")[1].strip()
			else:
				print("Please Connect  Ethernet Cable or Wi-Fi")
		# self.HOST_ADDRESS = "10.0.4.68"
		self.PORT = port
		self.HEADER_LENGTH = HEADER_LENGTH_
		self.MAX_CONNECTION = MAX_CONNECTION_
		self.current_directory = "./Local_server_files"
		self.instruction_length = INSTRUCTION_LENGTH_
		self.BUFFER = BUFFER_
		self.MAX_SIZE = self.BUFFER * 1024 * 1024
		self.server_socket = None
		self.PORT_RANGE = PORT_RANGE_

	def start_server(self):

		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.server_socket.bind((self.HOST_ADDRESS, self.PORT))
		self.server_socket.listen(self.MAX_CONNECTION)

		print(f"Server is running on {self.HOST_ADDRESS}:{self.PORT}")

	def send_requested_file(self, client_socket):
		file_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		print(f"file name length: {file_name_length}")
		file_name = client_socket.recv(file_name_length).decode('utf-8').strip()
		print(f"file_name: {file_name}")
		print(f"{file_name} is requested to download")

		# if file is a file
		if not os.path.isdir(self.current_directory + "/" + file_name):

			f = open(self.current_directory + "/" + file_name, 'rb')

			file_size = os.stat(self.current_directory + "/" + file_name).st_size
			client_socket.sendall(bytes(f"{file_size:<{self.HEADER_LENGTH}}", "utf-8"))

			print(f"size of file {file_size // (1024 * 1024)} MB!")

			total_data_send = 0
			for segments in range(file_size // self.MAX_SIZE):
				file_data = f.read(self.MAX_SIZE)
				# print(f"length of data we are gonna send: {len(file_data)//(1024*1024)} MB")

				server_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				server_socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

				server_socket_.bind((self.HOST_ADDRESS, self.PORT + 1 + segments%self.PORT_RANGE))
				server_socket_.listen(1)
				client_socket_ = server_socket_.accept()[0]
				client_socket_.sendall(file_data)
				server_socket_.close()
				total_data_send += self.MAX_SIZE
				print(f"Data Sent: {total_data_send // (1024 * 1024)} MB/{file_size // (1024 * 1024)} MB", end="\r")

			if file_size % self.MAX_SIZE != 0:
				file_data = f.read(file_size % self.MAX_SIZE)
				# print(f"length of data we are gonna send: {len(file_data)//(1024*1024)} MB")
				server_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				server_socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

				server_socket_.bind((self.HOST_ADDRESS, self.PORT + 1 + (file_size // self.MAX_SIZE)%self.PORT_RANGE))
				server_socket_.listen(1)
				client_socket_ = server_socket_.accept()[0]
				client_socket_.sendall(file_data)
				total_data_send += len(file_data)
				print(f"Data Sent: {total_data_send // (1024 * 1024)} MB/{file_size // (1024 * 1024)} MB", end="\r")

			f.close()
		# if file is a folder
		else:

			time.sleep(1)

		print(f"{file_name} has been sent!")

	def receive_file(self, client_socket):

		file_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		file_name = client_socket.recv(file_name_length).decode('utf-8')
		print(f"redirecting {file_name} to function Download_file")
		# Send an indicator to prepare server to send file
		print(f"{file_name} will be received from Client")
		receivable_file_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		print(f"receivable_file_length: {receivable_file_length // (1024 * 1024)} MB")
		f = open("./Local_server_files/copy_" + file_name, "wb")
		received_file_length = 0
		t0 = time.time()
		while receivable_file_length > received_file_length:
			received_data = client_socket.recv(receivable_file_length)
			length_received_data = len(received_data)
			t1 = time.time()
			if t1 - t0 > 1:
				a = received_file_length // (1024 * 1024)
				b = receivable_file_length // (1024 * 1024)
				print(f"length of data received: {a:>6} MB/{b:>6} MB", end="\r")
				t0 = t1
			received_file_length += length_received_data
			f.write(received_data)
		f.close()

	def remove_file(self, client_socket):

		file_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		print(f"file name length: {file_name_length}")
		file_name = client_socket.recv(file_name_length).decode('utf-8').strip()
		print(f"{file_name} is requested to be deleted")
		try:
			os.remove(os.path.join(self.current_directory, file_name))
			client_socket.sendall(b'1')
			print(f"{file_name} Successfully removed")
		except:
			client_socket.sendall(b'0')
			print(f"can not remove {file_name}")

	def rename_file(self, client_socket):

		file_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		print(f"file name length: {file_name_length}")
		file_name = client_socket.recv(file_name_length).decode('utf-8').strip()
		print(f"old file name: {file_name}")
		new_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		print(f"new file name length: {new_name_length}")
		new_name = client_socket.recv(new_name_length).decode('utf-8').strip()
		print(f"name of {file_name} is requested to change into {new_name}")

		try:
			os.rename(os.path.join(self.current_directory, file_name), os.path.join(self.current_directory, new_name))
			client_socket.sendall(b'1')
			print(f"{file_name} successfully renamed to {new_name}!")

		except:
			client_socket.sendall(b'0')
			print(f"Could not rename {file_name}!")

	# def Move_file(client_socket,)

	def send_file_list(self, client_socket):
		print("Inside the send_file_list function")
		file_name_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8').strip())
		# print(f"file_name_length: {file_name_length}")
		file_name = client_socket.recv(file_name_length).decode('utf-8').strip()
		print(f"file_name: {file_name}")
		file_list = os.listdir(file_name)
		# print(f"file List: {file_list}")
		pickled_file_list = pickle.dumps(file_list)
		client_socket.sendall(bytes(f"{len(pickled_file_list):<{self.HEADER_LENGTH}}", 'utf-8'))
		client_socket.sendall(pickled_file_list)

	def search_(self, current_directory, reg_ex_string):

		matching_list = []
		file_folder_list = os.listdir(current_directory)
		for file_name in file_folder_list:
			file_name_path = os.path.join(current_directory, file_name)
			if re.search(reg_ex_string, file_name):
				matching_list.append(file_name_path)
			if os.path.isdir(file_name_path):
				matching_list += self.search_(current_directory + '/' + file_name, reg_ex_string)
		return matching_list

	def return_search(self, client_socket):
		# Current Directory
		current_directory_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8'))
		current_directory = client_socket.recv(current_directory_length).decode('utf-8')
		# String
		string_length = int(client_socket.recv(self.HEADER_LENGTH).decode('utf-8'))
		string = client_socket.recv(string_length).decode('utf-8')

		reg_ex_string = re.compile(string, re.IGNORECASE)
		search_list = self.search_(current_directory, reg_ex_string)

		pickled_search_list = pickle.dumps(search_list)
		client_socket.sendall(bytes(f"{len(pickled_search_list):<{self.HEADER_LENGTH}}", 'utf-8'))
		client_socket.sendall(pickled_search_list)
