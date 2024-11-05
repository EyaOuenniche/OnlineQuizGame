import socket
import threading
import time

SERVER_IP = '192.168.1.22'
SERVER_PORT = 12345
clients = []
scores = {}
lock = threading.Lock()
current_question_index = 0
answered = False  # Global variable to track if a question has been answered

# Load questions
def load_questions(filename):
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            question, answer = line.strip().split('|')
            questions.append({"question": question, "answer": answer})
    return questions

quiz_questions = load_questions('Questions.txt')

# Setup server
def setup_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}")
    return server_socket

# Handle client connections and answers
def handle_client(client_socket, username):
    global answered
    scores[username] = 0
    clients.append((client_socket, username))
    print(f"{username} joined the game!")

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            with lock:
                check_answer(message, username)  # Check if the answer is correct
    except:
        print(f"{username} has left the game.")
    finally:
        clients.remove((client_socket, username))
        client_socket.close()

# Broadcast message to all clients
def broadcast(message):
    for client_socket, _ in clients:
        try:
            client_socket.send(message.encode())
        except:
            pass

# Start the quiz game
def start_quiz():
    global current_question_index, answered
    while current_question_index < len(quiz_questions):
        question = quiz_questions[current_question_index]
        answered = False  # Reset the answered flag for each question
        broadcast(f"Question: {question['question']}")
        start_time = time.time()

        # Wait up to 30 seconds for someone to answer correctly
        while time.time() - start_time < 30:
            with lock:
                if answered:
                    break
            time.sleep(1)  # Allow other threads to operate

        if not answered:
            broadcast(f"Time's up! The correct answer was: {question['answer']}")
        
        current_question_index += 1
        time.sleep(2)  # Pause before next question

    display_scores()  # End of quiz, display final scores

# Check client answer
def check_answer(answer, username):
    global answered
    if current_question_index < len(quiz_questions):
        current_question = quiz_questions[current_question_index]
        if answer.strip().lower() == current_question["answer"].lower():
            if not answered:
                scores[username] += 1
                answered = True  # Mark question as answered
                broadcast(f"{username} answered correctly and gets a point!")
                display_scores()

# Display scores
def display_scores():
    scores_message = "\n".join([f"{user}: {score}" for user, score in scores.items()])
    broadcast(f"Scores:\n{scores_message}")

def main():
    server_socket = setup_server()

    # Accept connections until 3 clients are connected
    while len(clients) < 3:
        client_socket, addr = server_socket.accept()
        username = client_socket.recv(1024).decode()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

    start_quiz()
    server_socket.close()

if __name__ == "__main__":
    main()
