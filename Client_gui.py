import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

# Server IP and Port
SERVER_IP = '192.168.50.203'
SERVER_PORT = 12345

# Initialize global variables
client_socket = None
username = None
question_end = False  # Flag to track if a question round has ended

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
    global question_end
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith("Question:"):
                question_end = False
                question_label.config(text=message)
                feedback_label.config(text="")
                start_timer(30)  # Start 30-second countdown for each question
            elif message.startswith("Time's up!") or "answered correctly first" in message:
                question_end = True
                feedback_label.config(text=message)
            elif "Final Results:" in message:
                display_final_results(message)  # Update the existing display with results

        except:
            print("Disconnected from server.")
            break

def start_timer(seconds):
    def countdown():
        for sec in range(seconds, 0, -1):
            timer_label.config(text=f"Time left: {sec} seconds")
            time.sleep(1)
        timer_label.config(text="Time left: 0 seconds")
    threading.Thread(target=countdown).start()

def submit_answer():
    global question_end
    if not question_end:  # Only allow submission if the question hasn't ended
        answer = answer_entry.get()
        client_socket.send(answer.encode())
        answer_entry.delete(0, tk.END)

def display_final_results(message):
    # Clear previous results before displaying new ones
    final_results_text.delete(1.0, tk.END)
    final_results_text.insert(tk.END, message)  # Display final results in the same window

# GUI Setup
root = tk.Tk()
root.title("Quiz Game")
root.geometry("500x400")
root.configure(bg="#add8e6")

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

# Timer display
timer_label = tk.Label(root, text="Time left: 30 seconds", font=("Arial", 12), bg="#add8e6")
timer_label.pack(pady=5)

# Score display
score_label = tk.Label(root, text="Score: 0", font=("Arial", 12), bg="#add8e6")
score_label.pack(pady=10)

# Feedback display
feedback_label = tk.Label(root, text="", font=("Arial", 12), bg="#add8e6")
feedback_label.pack(pady=10)

# Final results display area
final_results_text = tk.Text(root, height=8, width=50, bg="#add8e6", font=("Arial", 10))
final_results_text.pack(pady=10)

root.mainloop()
