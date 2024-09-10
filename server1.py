import socket
import threading
from deep_translator import GoogleTranslator


# Server setup 
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
LISTENER_LIMIT = 5
HEADER = 64
DISCONNECT_MESSAGE = '!DISCONNECT ME'
FORMAT = 'utf-8'


# Active clients list and lock for thread safety
_activeClients = list()
_clients_lock = threading.Lock()


# Languages
LANGUAGE_CODES = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Hindi': 'hi',
    'Chinese': 'zh',
    'Japanese': 'ja',
    'Arabic': 'ar',
    'Russian': 'ru',
    'Portuguese': 'pt'
}



# Function to translate the message into the target language
def translate_language(target, message):
    translator = GoogleTranslator(source='auto', target=target)
    try:
        return str(translator.translate(message))
    except Exception as e:
        print(f"Translation error: {e}")
        return message  # If translation fails, return the original message


# Function to keep listening to new incoming messages 
def listen_messages(client, name, language):
    while True:
        try:
            message = client.recv(2048).decode(FORMAT)
            if message == DISCONNECT_MESSAGE:
                remove_client(client)
                break
            if message != '':
                broadcast_messages(message, name, language)
        except Exception as e:
            print(f"Error receiving message: {e}")
            remove_client(client)
            break


# Function to send a message to a particular client
def msg_to_client(client, msg):
    try:
        client.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"Error sending message to client: {e}")


# Broadcasting messages to all connected clients
def broadcast_messages(message, name, language):
    # detect the language
    source_lang_code = LANGUAGE_CODES[language]
    
    with _clients_lock:
        for user in _activeClients:
            target_lang = user[0]['language']           # get the recepients selected language
            target_lang_code = LANGUAGE_CODES[target_lang]
            if target_lang_code != source_lang_code:
                trans_message = translate_language(target=target_lang_code, message=message)
            else:
                trans_message = message
            final_message = f"{name} ~ {trans_message}"
            msg_to_client(user[1], final_message)


# Function to remove a client upon disconnection
def remove_client(client):
    
    with _clients_lock:
        for user in _activeClients:
            if user[1] == client:
                _activeClients.remove(user)
                break
    client.close()


# Function to broadcast the join member message 
def broadcast_join_member_message(name):
    join_message = f'Hello Channel, Welcome our new member, {name}! :). \n {name} just joined Channel.'
    for user in _activeClients:
        target_lang = user[0]['language']           # get the recepients selected language
        target_lang_code = LANGUAGE_CODES[target_lang]
        if target_lang_code != 'en':
            trans_message = translate_language(target=target_lang_code, message=join_message)
        else:
            trans_message = join_message
        final_message = f"Channel ~ {trans_message}"
        msg_to_client(user[1], final_message)
            
            
# Function to handle clients
def handle_clients(client, address):
    print(f"[NEW CONNECTION] {address} connected.")  
 
    # Track the clients with their preference language and nickname
    username, language = client.recv(2048).decode(FORMAT).split('\n')  # Read username
    if username != '' and language != '':
        with _clients_lock:
            _activeClients.append(({'name': username, 'language': language}, client))
            print(_activeClients)
        
        # Broadcast the join message 
        broadcast_join_member_message(username)
         
        threading.Thread(target=listen_messages, args=(client, username, language,)).start()
    else:
        print("Username or Language is not provided")
        client.close()
            
    # except Exception as e:
    #     print(f"Error handling client: {e}")
    #     client.close()


def main():
    # Server socket setup
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the server socket
    server.bind(ADDR)
    
    # Server listens for accepting connectionsj requests from clients
    server.listen(LISTENER_LIMIT)
    print("[LISTENING] Server is listening...")
    
    while True:
        # If a client requests to connect, accept the request 
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]}:{address[1]}")

        threading.Thread(target=handle_clients, args=(client, address,)).start()


if __name__ == '__main__':
    main()
