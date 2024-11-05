import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server IP and Port
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

# Initialize global variables
client_socket = None
username = None
score = 0

def connect_to_server():
    global client_socket, username
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    username = username_entry.get()
    client_socket.send(username.encode())
    messagebox.showinfo("Connected", f"Connected as {username}")
    start_receiving()

def start_receiving():
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

def receive_messages():
    global score
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith("Question:"):
                question_label.config(text=message)
                feedback_label.config(text="")
            elif message.startswith("Scores:"):
                score = int(message.split(username + ": ")[1].split()[0])
                score_label.config(text=f"Score: {score}")
            else:
                feedback_label.config(text=message)
        except:
            print("Disconnected from server.")
            break

def submit_answer():
    answer = answer_entry.get()
    client_socket.send(answer.encode())
    answer_entry.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Quiz Game")
root.geometry("500x400")
root.configure(bg="#add8e6")  # Light blue background

# Username entry
tk.Label(root, text="Enter your username:", bg="#add8e6").pack(pady=10)
username_entry = tk.Entry(root)
username_entry.pack()

# Connect button
connect_button = tk.Button(root, text="Connect", command=connect_to_server, bg="#4CAF50", fg="white")
connect_button.pack(pady=10)

# Question display
question_label = tk.Label(root, text="Waiting for question...", font=("Arial", 14), bg="#add8e6")
question_label.pack(pady=20)

# Answer entry
tk.Label(root, text="Your Answer:", bg="#add8e6").pack()
answer_entry = tk.Entry(root)
answer_entry.pack()

# Submit button
submit_button = tk.Button(root, text="Submit Answer", command=submit_answer, bg="#4CAF50", fg="white")
submit_button.pack(pady=10)

# Score display
score_label = tk.Label(root, text="Score: 0", font=("Arial", 12), bg="#add8e6")
score_label.pack(pady=10)

# Feedback display
feedback_label = tk.Label(root, text="", font=("Arial", 12), bg="#add8e6")
feedback_label.pack(pady=10)

root.mainloop()