import socket
import threading

board = [' ' for _ in range(9)]
current_turn = 'X'
players = {}
turn_notified = {}

def print_board():
    board_str = f"{board[0]}|{board[1]}|{board[2]}\n-+-+-\n{board[3]}|{board[4]}|{board[5]}\n-+-+-\n{board[6]}|{board[7]}|{board[8]}"
    print(board_str)
    return board_str

def check_winner():
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] != ' ':
            return board[i]
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] != ' ':
            return board[i]
    if board[0] == board[4] == board[8] != ' ':
        return board[0]
    if board[2] == board[4] == board[6] != ' ':
        return board[2]
    return None

def broadcast(message):
    for client_socket in players.keys():
        try:
            client_socket.send(message.encode())
        except BrokenPipeError:
            pass  # Client disconnected

def handle_client(client_socket, addr, player):
    global current_turn
    players[client_socket] = player
    turn_notified[client_socket] = False
    try:
        client_socket.send(f"Welcome Player {player}! You are '{player}'.\n".encode())
        while True:
            if current_turn == player:
                turn_notified[client_socket] = False  # Reset flag for the player's turn
                client_socket.send("Your turn. Enter your move (0-8): ".encode())
                move = client_socket.recv(1024).decode()
                if not move.isdigit() or not 0 <= int(move) < 9 or board[int(move)] != ' ':
                    client_socket.send("Invalid move! Try again.\n".encode())
                else:
                    board[int(move)] = current_turn
                    broadcast(f"Player {player} made a move: {move}\n")
                    winner = check_winner()
                    if winner:
                        board_str = print_board()
                        broadcast(f"{board_str}\n{winner} wins!\n")
                        break
                    current_turn = 'O' if current_turn == 'X' else 'X'
                    board_str = print_board()
                    broadcast(f"{board_str}\nPlayer {current_turn}'s turn.\n")
            else:
                if not turn_notified[client_socket]:
                    client_socket.send("Wait for your turn.\n".encode())
                    turn_notified[client_socket] = True  # Set flag to indicate message has been sent
    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Connection with {addr} lost.")
    finally:
        client_socket.close()
        del players[client_socket]
        del turn_notified[client_socket]

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(2)
    print("Server started. Waiting for connections...")

    player = 'X'
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} has been established.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, player))
        client_thread.start()
        player = 'O' if player == 'X' else 'X'

if __name__ == "__main__":
    main()
