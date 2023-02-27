import socket
import threading

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'q':
                break
            print(f"Received message from client: {message}")
        except:
            break

    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen()

    #print("Server is listening on port 9999...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        receive_thread = threading.Thread(target=handle_client, args=(client_socket,))
        receive_thread.start()

        send_thread = threading.Thread(target=send_message, args=(client_socket,))
        send_thread.start()

def send_message(client_socket):
    while True:
        #message = input("Message: ")
        message = input()
        client_socket.send(message.encode('utf-8'))
        if message == 'q':
            break

    client_socket.close()

if __name__ == '__main__':
    main()
