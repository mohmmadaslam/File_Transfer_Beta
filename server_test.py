from server import Server

server = Server(4444)

server.start_server()
print("trying to connect to clients")

Client_socket, Client_Address = server.server_socket.accept()
print(f"Connection has been established with {Client_Address}")
Instruction = Client_socket.recv(server.instruction_length).decode('utf-8').strip()
server.send_file_list(Client_socket)
Instruction = Client_socket.recv(server.instruction_length).decode('utf-8').strip()
server.send_requested_file(Client_socket)