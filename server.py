import socket
import threading
import select
from PIL import Image
import time

def convert_to_ascii_art(image, output_width=50):
    # Skonwertuj obraz na skalę szarości
    image = image.convert('L')

    # Zdefiniuj listę znaków ASCII, które będą reprezentować różne poziomy jasności
    ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

    # Oblicz wysokość obrazu na podstawie proporcji
    width, height = image.size
    output_height = int(height / width * output_width)
    image = image.resize((output_width, output_height))

    # Podziel obraz na bloki pikseli i zamień każdy blok na odpowiadający mu znak ASCII
    ascii_art = ''
    for i in range(0, output_height, 1):
        for j in range(0, output_width, 1):
            pixel_value = 255 - image.getpixel((j, i))
            ascii_index = int(pixel_value / 25)
            ascii_char = ascii_chars[ascii_index]
            ascii_art += ascii_char
        ascii_art += '\r\n'
    #print(ascii_art)
    return ascii_art

def handle_client(client_socket, clients_list):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'q':
                break
            else:
                print(message)
                for other_client_socket in clients_list:
                    if other_client_socket != client_socket:
                        try:
                            other_client_socket.send(message.encode('utf-8'))
                        except:
                            clients_list.remove(other_client_socket)
                            other_client_socket.close()
        except:
            break

    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen()

    print("Server is listening on port 9999...")
    clients_list = []

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        clients_list.append(client_socket)

        receive_thread = threading.Thread(target=handle_client, args=(client_socket, clients_list))
        receive_thread.start()

        send_thread = threading.Thread(target=send_message, args=(client_socket, clients_list))
        send_thread.start()


def send_message(client_socket, clients):
    while True:
        message = input()

        if message == 'q':
            break
        elif message.startswith('send_file'):
            # Pobierz nazwę pliku z wiadomości
            filename = message.split()[1]

            # Wczytaj plik graficzny
            img = Image.open(filename)

            # Konwertuj obraz na ASCII-art
            ascii_art = convert_to_ascii_art(img)

            # Prześlij ASCII-art do wszystkich klientów
            for line in ascii_art.split('\n'):
                if line:
                    for c in clients:
                        #if c != client_socket:
                            c.send(line.encode('utf-8'))
                            time.sleep(0.02)  # opóźnienie dla lepszej czytelności
        else:
            # Prześlij wiadomość do wszystkich klientów (oprócz tego, który ją wysłał)
            for c in clients:
                #if c != client_socket:
                    c.send(message.encode('utf-8'))

    client_socket.close()

if __name__ == '__main__':
    main()
