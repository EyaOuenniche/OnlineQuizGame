import socket
import threading
import time
SERVER_IP = '127.0.0.1'  
SERVER_PORT = 12345
clients = []
scores = {}

def load_questions(filename):
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            question, answer = line.strip().split('|')
            questions.append({"question": question, "answer": answer})
    return questions

quiz_questions = load_questions('Questions.txt')

def setup_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}")
    return server_socket

def handle_client(client_socket, username):
    scores[username] = 0
    clients.append((client_socket, username))
    print(f"{username} joined the game!")
    while True:
        try:
            message = client_socket.recv(1024).decode()
           
            check_answer(message, username)
        except:
           
            print(f"{username} has left the game.")
            clients.remove((client_socket, username))
            break
def broadcast(message):
    for client_socket, _ in clients:
        client_socket.send(message.encode())

def start_quiz():
    for question in quiz_questions:
        broadcast(f"Question: {question['question']}")
        start_time = time.time()
        answered = False

        while time.time() - start_time < 30:  
            if answered:
                break

        
        if not answered:
            broadcast(f"Time's up! The correct answer was: {question['answer']}")
    display_scores()

def check_answer(answer, username):
    if answer == quiz_questions[0]["answer"]:
        scores[username] += 1
        broadcast(f"{username} got it right!")

def display_scores():
    scores_message = "\n".join([f"{user}: {score}" for user, score in scores.items()])
    broadcast(f"Scores:\n{scores_message}")


def main():
    server_socket = setup_server()
    while len(clients) < 3:
        client_socket, addr = server_socket.accept()
        username = client_socket.recv(1024).decode()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

    start_quiz()
    server_socket.close()
