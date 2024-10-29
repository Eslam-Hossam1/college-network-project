import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5555))

    while True:
        response = client.recv(1024).decode()
        print(response)
        if "wins" in response:
            break
        if "Your turn" in response:
            move = input("Enter your move (0-8): ")
            client.send(move.encode())
            
    client.close()

if __name__ == "__main__":
    main()
