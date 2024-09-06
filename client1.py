import socket
import threading

# SERVER - CLIENT SETUP
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'



# Function to send message
def send_message_to_server(client):
    while True:
        
        message = input('\nMessage: ')
        if message:
            client.sendall(message.encode())
        else:
            print("message not send, Try again")
            

# Function to keep listening for new incomming message from the server
def listen_msg_from_server(client):
    while True:
        response = client.recv(2048).decode(FORMAT)
        if response:
            username = response.split(' ~ ')[0]
            message = response.split(' ~ ')[1]
            
            print(f"[{username}]: {message}")
        else:
            print("No Message received from client")
            break
            

# Function to communicate with server
def communicate_to_server(client):
    
    # pass the usernam
    username = input("Enter Name: ")
    if len(username) > 3:
        client.sendall(username.encode())
    else:
        print("Your name, please.")
    
    # pass user's preferred langaugae
    language = input("Enter language symbol: ")
    if len(language) > 0:
        client.sendall(language.encode())
    else:
        print("Enter your preferred language to chat, Please:/")
        exit(0)
    
    threading.Thread(target=listen_msg_from_server,args = (client,)).start() 
        
    # send message 
    send_message_to_server(client)
    
        
# main function
def main():
    
    # Setup client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect the client socket to server socket
    client.connect(ADDR)
    print("Client Sucessfully connected to server!")
    
    # Start communicating with other client (through server ofc)
    communicate_to_server(client)
    
    
if __name__ == '__main__':
    main()