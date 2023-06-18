import socket
import pygame

# Define client parameters
HOST = '192.168.1.4'  # Server IP address
PORT = 5000  # Port number

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")

# Load track image
track_image = pygame.image.load(r'C:\Users\mebra\OneDrive\Desktop\Car Race\img\track.png')  # Replace 'track.png' with the actual image path

# Load car image
car_image = pygame.image.load(r'C:\Users\mebra\OneDrive\Desktop\Car Race\img\Car.png')  # Replace 'car.png' with the actual image path

chat_input = ''

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)  # Limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if chat_input:
                    try:
                        client_socket.sendall(f"CHAT:{chat_input}".encode())
                        chat_input = ''
                    except Exception as e:
                        print(f"Error occurred while sending chat message: {e}")
            elif event.key == pygame.K_BACKSPACE:
                chat_input = chat_input[:-1]
            else:
                chat_input += event.unicode

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_input = 'UP'
    elif keys[pygame.K_DOWN]:
        player_input = 'DOWN'
    elif keys[pygame.K_LEFT]:
        player_input = 'LEFT'
    elif keys[pygame.K_RIGHT]:
        player_input = 'RIGHT'
    else:
        player_input = ''

    if player_input:
        client_socket.sendall(player_input.encode())

    # Receive game updates from the server
    try:
        game_state = client_socket.recv(1024).decode()

        # Process game state updates
        game_state_data = game_state.split(';')
        player_positions = [tuple(map(int, pos.split(','))) for pos in game_state_data[0].split(':')[1].split(',')]
        player_scores = [int(score) for score in game_state_data[1].split(':')[1].split(',')]

        # Update the game window with the new positions and scores
        win.fill((255, 255, 255))  # Clear the screen

        # Draw the track
        win.blit(track_image, (0, 0))

        # Draw player cars
        for i, pos in enumerate(player_positions):
            # Draw the car image at the player's position
            car_rect = car_image.get_rect(center=pos)
            win.blit(car_image, car_rect)

        # Display player scores
        font = pygame.font.SysFont(None, 24)
        text1 = font.render(f"Player 1 Score: {player_scores[0]}", True, (0, 0, 0))
        text2 = font.render(f"Player 2 Score: {player_scores[1]}", True, (0, 0, 0))
        win.blit(text1, (10, 10))
        win.blit(text2, (10, 40))
        
        # Display chat input box
        pygame.draw.rect(win, (255, 255, 255), (10, 550, 780, 40))
        pygame.draw.rect(win, (0, 0, 0), (10, 550, 780, 40), 2)
        font = pygame.font.SysFont(None, 24)
        text = font.render(chat_input, True, (0, 0, 0))
        win.blit(text, (20, 560))

        pygame.display.update()
    except ConnectionResetError:
        print("The server has closed the connection.")
        running = False

    except Exception as e:
        print(f"Error occurred during receiving game state: {e}")
        running = False

# Clean up resources
pygame.quit()
client_socket.close()