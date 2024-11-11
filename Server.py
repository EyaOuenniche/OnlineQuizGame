import socket
import threading
import time

SERVER_IP = '192.168.1.104'
SERVER_PORT = 12345
clients = []
scores = {}
lock = threading.Lock()
current_question_index = 0
first_correct_answer = None  # Track the first player to answer correctly

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
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}")
    return server_socket

# Handle client connections and answers
def handle_client(client_socket, username):
    scores[username] = 0
    clients.append((client_socket, username))
    print(f"{username} joined the game!")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            with lock:
                check_answer(message, username)  
        except:
            print(f"{username} has left the game.")
            clients.remove((client_socket, username))
            break

# Broadcast message to all clients
def broadcast(message):
    for client_socket, _ in clients:
        client_socket.send(message.encode())
        
#Send score to each client individually
def send_individual_score(client_socket, username):
    message = f"Your score: {scores[username]}"
    client_socket.send(message.encode())

# Start the quiz game
def start_quiz():
    global current_question_index
    while current_question_index < len(quiz_questions):
        question = quiz_questions[current_question_index]
        global first_correct_answer
        first_correct_answer = None  
        broadcast(f"Question: {question['question']}")
        start_time = time.time()

        while time.time() - start_time < 30:
            time.sleep(1)  

        if first_correct_answer is None:
            broadcast(f"Time's up! The correct answer was: {question['answer']}")
        else:
            broadcast(f"{first_correct_answer} answered correctly first!")
        
        for client_socket, username in clients:
            send_individual_score(client_socket, username)

        current_question_index += 1
        time.sleep(2)  

    print("All questions complete, displaying final leaderboard...")
    display_final_scores()  

# Check client answer
def check_answer(answer, username):
    global first_correct_answer
    if current_question_index < len(quiz_questions):
        current_question = quiz_questions[current_question_index]
        if answer.strip().lower() == current_question["answer"].lower():
            if first_correct_answer is None:  
                first_correct_answer = username  
                scores[username] += 1  
                broadcast(f"{username} answered correctly!")

# Display final scores
def display_final_scores():
    print("Displaying final leaderboard...")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    final_scores_message = "🏆 Final Results:\n"
    podium_positions = ["🥇 First Place: ", "🥈 Second Place: ", "🥉 Third Place: "]

    for idx, (user, score) in enumerate(sorted_scores):
        if idx < 3:
            final_scores_message += f"{podium_positions[idx]} {user} with {score} points\n"
        else:
            final_scores_message += f"{user}: {score} points\n"

    broadcast(final_scores_message)

def main():
    server_socket = setup_server()

    # Accept connections until 3 clients are connected
    while len(clients) < 3:
        client_socket, addr = server_socket.accept()
        username = client_socket.recv(1024).decode()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

    # Start the quiz
    start_quiz()
    server_socket.close()

if __name__ == "__main__":
    main()
