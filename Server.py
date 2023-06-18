import socket
import threading
import random
import pygame

# Define game server parameters
HOST = '0.0.0.0'  # Server IP address
PORT = 5000  # Port number

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)  # Allow up to 2 players

players = []  # Store connected player sockets

# Game state variables
player_names = []  # Store player names
player_positions = [(100, 300), (400, 300)]  # Initial positions of players
player_scores = [0, 0]  # Scores of players
player_cars = []  # Cars for each player

# Define colors for players' cars
CAR_COLORS = [(255, 0, 0), (0, 0, 255)]  # Red and blue

# Load car image
car_image = pygame.image.load("D:\Car Racing Game using Pygame\Car Race\img\Car.png")  # Replace 'car.png' with the actual image path

def handle_client(player_socket, player_id):
    # Handle individual player connection
    while True:
        try:
                # Receive player input from the client
            data = player_socket.recv(1024).decode()
            if not data:
                break
        
        
            if data.startswith('NAME:'):
                player_name = data.split(':')[1]
                player_names.append(player_name)
                player_socket.sendall("Welcome to the game!".encode())
                broadcast(f"{player_name} has joined the game.")
            elif data.startswith('CHAT:'):
                chat_msg = data.split(':')[1]
                broadcast(f"{player_names[player_id]}: {chat_msg}")

            # Process player input and update game state
            if data == 'UP':
                player_positions[player_id] = (player_positions[player_id][0], player_positions[player_id][1] - 5)
            elif data == 'DOWN':
                player_positions[player_id] = (player_positions[player_id][0], player_positions[player_id][1] + 5)
            elif data == 'LEFT':
                player_positions[player_id] = (player_positions[player_id][0] - 5, player_positions[player_id][1])
            elif data == 'RIGHT':
                player_positions[player_id] = (player_positions[player_id][0] + 5, player_positions[player_id][1])

            # Check collision detection
            if player_positions[player_id][0] < 0 or player_positions[player_id][0] > 800 \
                    or player_positions[player_id][1] < 0 or player_positions[player_id][1] > 600:
                # Collision occurred, deduct score
                player_scores[player_id] -= 1
                player_positions[player_id] = (100, 300)  # Reset position after collision

            # Update scores
            player_scores[player_id] += 1  # Increment score for each update

            # Send game updates to the players
            game_state = f"POS:{player_positions[0]},{player_positions[1]};SCORE:{player_scores[0]},{player_scores[1]}"
            for p in players:
                if p != player_socket:
                    p.sendall(game_state.encode())

            # Check game end condition and break the loop if necessary
        
        except ConnectionResetError:
            # Handle disconnection or connection reset by the client
            print(f"Player {player_id} disconnected.")
            players.remove(player_socket)
            if player_names:
                player_names.pop(player_id)
            if player_positions:
                player_positions.pop(player_id)
            if player_scores:
                player_scores.pop(player_id)
            if player_cars:
                player_cars.pop(player_id)
            broadcast(f"Player {player_id+1} has left the game.")
            break

        except Exception as e:
            print(f"Error occurred for player {player_id}: {e}")
            break
        
def broadcast(message):
    # Send a message to all connected players
    for p in players:
        p.sendall(message.encode())


def accept_connections():
    # Accept incoming player connections
    player_id = 0
    while True:
        player_socket, addr = server_socket.accept()
        players.append(player_socket)
        print('Player connected:', addr)

        # Randomly assign a car color to the player
        car_color = CAR_COLORS[player_id]
        player_cars.append(car_color)

        threading.Thread(target=handle_client, args=(player_socket, player_id)).start()
        player_id += 1


# Start accepting connections
print('Waiting for players...')
threading.Thread(target=accept_connections).start()