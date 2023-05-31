import socket
import threading

class GameServer:
    def __init__(self, host, port):
        self.host =host
        self.port = port
        self.players = {} # Dictionary to store player information
        self.game_state = {} # Dictionary to store game state
        self.lock = threading.Lock() # Lock to ensure thread safety

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

        print(f"Server started on {self.host}:{self.port}")

        while True:
            conn, addr = self.sock.accept()
            print(f"New client connected: {addr}")

            # Start a new thread to handle the client connection
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def handle_client(self, conn, addr):
        with self.lock:
            # Add the new player to the players dictionary
            self.players[addr] = conn

        while True:
            # Receive messages from the client
            data = conn.recv(1024)
            if not data:
                break

            # Parse the message
            message = data.decode()
            parts = message.split(":")
            command = parts[0]

            # Handle the message based on the command
            if command == "JOIN":
                # Add the player to the game state
                with self.lock:
                    self.game_state[addr] = {"x": 0, "y": 0}
                self.broadcast(f"PLAYER{addr} joined the game")

            elif command == "MOVE":
                # Update the player's position in the game state
                with self.lock:
                    self.game_state[addr]["x"] = int(parts[1])
                    self.game_state[addr]["y"] = int(parts[2])

            elif command == "CHAT":
                # Broadcast the message to all players
                message = f"CHAT:{addr}:{parts[1]}"
                self.broadcast(message)

        # Remove the player from the game state and players dictionary
        with self.lock:
            del self.players[addr]
            del self.game_state[addr]
        conn.close()
        print(f"Client disconnected: {addr}")

    def broadcast(self, message):
        # Send a message to all connected players
        with self.lock:
            for player in self.players.values():
                player.sendall(message.encode())

if __name__ == "__main__":
    server = GameServer("localhost", 5000)
    server.start()