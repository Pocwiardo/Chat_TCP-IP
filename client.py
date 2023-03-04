
import socket
import threading
import select
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog
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




class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Utwórz okno
        self.setWindowTitle('Chat')
        self.setGeometry(100, 100, 800, 600)

        # Utwórz widgety
        self.message_history = QTextEdit()
        self.message_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.send_file_button = QPushButton('Send File')

        # Stwórz layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.message_history)

        hbox = QHBoxLayout()
        hbox.addWidget(self.message_input)
        hbox.addWidget(self.send_button)
        hbox.addWidget(self.send_file_button)

        vbox.addLayout(hbox)

        # Ustaw layout
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        # Połącz sygnały z slotami
        self.send_button.clicked.connect(self.send_message)
        self.send_file_button.clicked.connect(self.send_file)

        # Utwórz gniazdo sieciowe
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(('localhost', 9999))

        # Utwórz wątek odbierający dane z serwera
        self.receive_thread = threading.Thread(target=self.handle_server)
        self.receive_thread.start()

    def handle_server(self):
        while True:
            try:
                # Użyj funkcji select, aby oczekiwać na dane do odczytu z serwera
                ready_to_read, _, _ = select.select([self.server_socket], [], [], 0.1)
                if self.server_socket in ready_to_read:
                    message = self.server_socket.recv(1024).decode('utf-8')
                    if message == 'q':
                        break

                    # Dodaj otrzymaną wiadomość do historii wiadomości
                    self.message_history.append(message)
            except:
                break

        self.server_socket.close()
        sys.exit()

    def send_message(self):
        # Pobierz treść wiadomości z pola tekstowego
        message = self.message_input.text()

        if message == 'q':
            # Zamknij połączenie sieciowe i wyjdź z aplikacji
            self.server_socket.send(message.encode('utf-8'))
            self.server_socket.close()
            sys.exit()
        elif message:
            # Wyślij wiadomość do serwera
            self.server_socket.send(message.encode('utf-8'))

        # Wyczyść pole tekstowe
        self.message_input.clear()

    def send_file(self):
        # Pobierz nazwę pliku z pola tekstowego
        #filename = self.message_input.text()
        filename, _ = QFileDialog.getOpenFileName(self, 'Przeglądaj', '/', "Obrazy (*.png *.jpg *.jpeg)")
        #print(filename)
        if filename:
            try:
                # Wczytaj plik graficzny
                img = Image.open(filename)

                # Konwertuj obraz na ASCII-art
                ascii_art = convert_to_ascii_art(img)

                # Prześlij ASCII-art do serwera
                for line in ascii_art.split('\n'):
                    if line:
                        self.server_socket.send(line.encode('utf-8'))
                        time.sleep(0.02)  # opóźnienie dla lepszej czytelności
            except:
                print("aaa")

        # Wyczyść pole tekstowe
        self.message_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = ChatWindow()
    main_window.show()

    sys.exit(app.exec_())
