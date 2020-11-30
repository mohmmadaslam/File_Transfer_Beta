from client import Client

client = Client()
client.HOST_ADDRESS = input("Enter Server IP: ")


def start_client_and_talk_to_server():

	client.connect_to_server()
	print("Successfully connected")

	while True:

		client.refresh_current_hiararcy()

		print("Refreshed_Hierarchy")
		# print(f"Port Id after refreshed hierarchy : {client.PORT}")
		print("1:Request a file")
		print("2:Upload a file")
		print("3:Remove a file")
		print("4:Rename a file")
		print("5:Back")
		print("6:Forward")
		print("7:Enter in a folder")
		print("8:Search a file")

		action = int(input())
		
		if action == 1:
			
			client.download_file()

		elif action == 2:

			client.upload_file()

		elif action == 3:
			
			client.remove_file()

		elif action == 4:

			client.rename_file()

		elif action == 5:
			
			client.back()

		elif action == 6:
			
			client.forward()

		elif action == 7:
			
			client.access_folder()

		elif action == 8:
			
			client.search()

		else:
			print("please enter correct number!")

start_client_and_talk_to_server()
