import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror


# SERVER - CLIENT SETUP
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'


# Setup client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# User Interface
root = tk.Tk()
root.geometry('885x670')
root.title('ChatEZ')
root.resizable(False,False)


# Styling components
header_color = '#74c69d'
chat_area_color = '#d8f3dc'
message_area_color = '#40916c'
username_label_color_bg = '#52b788'
username_label_color_fg = '#161a1d'
username_textbox_color_bg = '#b7e4c7'
username_textbox_color_fg = '#161a1d'
join_button_color_bg = '#1b4332'
join_button_color_fg = '#74c69d'
text_area_color_bg = '#a4c3b2'
text_area_color_fg = '#161a1d'
send_button_color_bg = '#161a1d'
send_button_color_fg = '#52b788'
message_text_bg = '#d8f3dc'
message_text_fg = '#52b788'


# Fonts
FONT = ('Helvetica', 15)
SMALL_FONT = ('Helvetica', 15)


# Function to updates the message onto the chat area
def add_message(message, alignment='left'):
    message_box.config(state=tk.NORMAL)
    if alignment == 'left':
        message_box.insert(tk.END, message + '\n', 'left_align')
    else:
        message_box.insert(tk.END, message + '\n', 'right_align')

    message_box.config(state=tk.DISABLED)
    message_box.yview(tk.END)       # automatic scroll to the end
    
    
# Function to set up tags for alignment
def setup_tags():
    message_box.tag_configure('left_align', justify='left', lmargin1=10, lmargin2=10)
    message_box.tag_configure('right_align', justify='right', rmargin=10)
    

# Event Handling Functions
def _connect():
    try:
        # connect client to server
        client.connect(ADDR)
    except:
        showerror('Connection Error :/',f'Unable to connect the client {client} to server {SERVER} {PORT}')
        exit(0)

    username = username_textbox.get()
    if len(username) > 3:
        print(username)
        client.sendall(username.encode())
    else:
        # print("Your name, please.")
        showerror('Invalid Username', 'Username cannot be empty :/')
    
    # pass user's preferred langaugae
    language = language_dropdown.get()
    if len(language) > 0:
        print(language)
        client.sendall(language.encode())
    else:
        showerror('Invalid Language Selection', 'Language cannot be empty and outside from given option  :/')
        exit(0)
    
    # join_message = f'Hello Channel, Welcome our new member, {username}! :). \n {username} just joined Channel.'
    # add_message(join_message)
    threading.Thread(target=listen_msg_from_server,args = (client,)).start()


def send_message():
    message = text_area.get()
    if message:
        client.sendall(message.encode())
    else:
        showerror('Empty Message :/',"Message cannot be empty")


# Layout Configure
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=5)
root.rowconfigure(2, weight=1)


# Design the chat Widget
header_frame = tk.Frame(root, width=600, height=70, bg=header_color)
header_frame.grid(row=0, column=0, sticky=tk.NSEW)


chats = tk.Frame(root, width=600, height=500, bg=chat_area_color)
chats.grid(row=1, column=0, sticky=tk.NSEW)


message_text = tk.Frame(root, width=600, height=50, bg=message_area_color)
message_text.grid(row=2, column=0, sticky=tk.NSEW)


# Chat Joining Parameters
username_label = tk.Label(header_frame, text='Name:', font=FONT, bg=header_color, fg=username_label_color_fg)
# username_label = tk.Label(header_frame, text='Name:', font=FONT, fg=username_label_color_fg)
username_label.pack(side=tk.LEFT, padx=15, pady=10)


username_textbox = tk.Entry(header_frame, font=FONT, bg=username_textbox_color_bg, width=23)
username_textbox.pack(side=tk.LEFT,padx=15, pady=10)


# Language selection dropdown
language_label = tk.Label(header_frame, text="Language:", font=FONT, bg=header_color)
language_label.pack(side=tk.LEFT, padx=15, pady=10)


language_var = tk.StringVar()
language_dropdown = ttk.Combobox(header_frame, textvariable=language_var, font=FONT, background=username_textbox_color_bg)
language_dropdown['values'] = ('English', 'Spanish', 'French', 'German', 'Hindi', 
                               'Chinese', 'Japanese', 'Arabic', 'Russian', 'Portuguese')
language_dropdown.pack(side=tk.LEFT, padx=15, pady=10)


# Joining Button
join_button = tk.Button(header_frame, text='Join', font=FONT, bg= join_button_color_bg, fg=join_button_color_fg, command=_connect)
join_button.pack(side=tk.RIGHT,padx=15, pady=10)


# Message sending text area
text_area = tk.Entry(message_text,font=FONT, bg=text_area_color_bg, fg=text_area_color_fg, width=70)
text_area.pack(side=tk.LEFT, padx=15, pady=5)


# Text sending button
send_button = tk.Button(message_text, text='Send', font=FONT, bg=send_button_color_bg, fg=send_button_color_fg, command=send_message)
send_button.pack(side=tk.RIGHT, padx=10, pady=5)


# Chat Area
message_box = ScrolledText(chats, font=SMALL_FONT, bg=message_text_bg, fg=message_text_fg, width=77, height=25)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP, padx=10, pady=10)


# Function to keep listening for new incomming message from the server
def listen_msg_from_server(client):
    while True:
        response = client.recv(2048).decode(FORMAT)
        if response:
            username = response.split(' ~ ')[0]
            message = response.split(' ~ ')[1]
            final_message = f'[{username}]: {message}'
            add_message(final_message)
        else:
            showerror('Error:/',"No Message received from client")
            break
            
            
# main function
def main():
    # UI
    root.mainloop()
    
    
if __name__ == '__main__':
    main()