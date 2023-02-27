import socket
import threading

def handle_server(server_socket):
    while True:
        try:
            message = server_socket.recv(1024).decode('utf-8')
            if message == 'q':
                break
            print(f"Received message from server: {message}")
        except:
            break

    server_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('localhost', 9999))
    #print("Connected to server...")

    receive_thread = threading.Thread(target=handle_server, args=(server_socket,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_message, args=(server_socket,))
    send_thread.start()

def send_message(server_socket):
    while True:
        #message = input("Message: ")
        message = input()
        server_socket.send(message.encode('utf-8'))
        if message == 'q':
            break

    server_socket.close()

if __name__ == '__main__':
    main()
