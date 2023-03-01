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
        ascii_art += '\n'
    #print(ascii_art)
    return ascii_art

def handle_server(server_socket):
    while True:
        try:
            # Użyj funkcji select, aby oczekiwać na dane do odczytu z serwera
            ready_to_read, _, _ = select.select([server_socket], [], [], 0.1)
            if server_socket in ready_to_read:
                message = server_socket.recv(1024).decode('utf-8')
                if message == 'q':
                    break
                #print(f"Received message from server: {message}")
                print(message)
        except:
            break

    server_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('localhost', 9999))

    receive_thread = threading.Thread(target=handle_server, args=(server_socket,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_message, args=(server_socket,))
    send_thread.start()

def send_message(server_socket):
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

            # Prześlij ASCII-art do serwera
            #print(ascii_art)
            for line in ascii_art.split('\n'):
                if line:
                    server_socket.send(line.encode('utf-8'))
                    time.sleep(0.02)  # opóźnienie dla lepszej czytelności
                    #server_socket.send('\n'.encode('utf-8'))
        else:
            server_socket.send(message.encode('utf-8'))

    server_socket.close()

if __name__ == '__main__':
    main()
