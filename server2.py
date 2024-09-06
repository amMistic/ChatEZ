import socket
import threading
from deep_translator import GoogleTranslator

# Server setup 
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
LISTENER_LIMIT = 5
HEADER = 64
DISCONNECT_MESSAGE = '!DISCONNECT'
FORMAT = 'utf-8'

_activeClients = []
_clients_lock = threading.Lock()



def translate_language(target, message):
    translator = GoogleTranslator(source='auto', target=target)
    try:
        return translator.translate(message)
    except Exception as e:
        print(f"Translation error: {e}")
        return message

def listen_messages(client, name, language):
    while True:
        try:
            message = client.recv(2048).decode(FORMAT)
            if message == DISCONNECT_MESSAGE:
                remove_client(client)
                break
            if message:
                broadcast_messages(message, name, language)
        except:
            remove_client(client)
            break

def msg_to_client(client, msg):
    try:
        client.sendall(msg.encode(FORMAT))
    except Exception as e:
        print(f"Error sending message to client: {e}")

def broadcast_messages(message, name, language):
    source_language = language
    with _clients_lock:
        for user in _activeClients:
            target_lang = user[0]['language']
            if target_lang != source_language:
                trans_message = translate_language(target=target_lang, message=message)
            else:
                trans_message = message
            final_message = f"{name} ~ {trans_message}"
            msg_to_client(user[1], final_message)

def remove_client(client):
    with _clients_lock:
        for user in _activeClients:
            if user[1] == client:
                _activeClients.remove(user)
                break
    client.close()

def handle_clients(client, address):
    print(f"[NEW CONNECTION] {address} connected.")  
    try:
        username = client.recv(2048).decode(FORMAT)
        language = client.recv(2048).decode(FORMAT)
        if username and language:
            with _clients_lock:
                _activeClients.append(({'name': username, 'language': language}, client))
            threading.Thread(target=listen_messages, args=(client, username, language,)).start()
        else:
            client.close()
    except Exception as e:
        print(f"Error handling client: {e}")
        client.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(LISTENER_LIMIT)
    print("[LISTENING] Server is listening...")
    
    while True:
        client, address = server.accept()
        threading.Thread(target=handle_clients, args=(client, address,)).start()

if __name__ == '__main__':
    main()
