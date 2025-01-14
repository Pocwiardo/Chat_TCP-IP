
import socket
import threading
import select
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt
from PIL import Image
import time
import os

def convert_to_ascii_art(image, output_width=50):
    image = image.convert('L')

    ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

    width, height = image.size
    output_height = int(height / width * output_width)
    image = image.resize((output_width, output_height))

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




class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Chat')
        self.setGeometry(100, 100, 800, 600)

        self.message_history = QTextEdit()
        self.message_input = QLineEdit()
        self.message_history.setReadOnly(True)
        self.send_button = QPushButton('Send')
        self.send_file_button = QPushButton('Send Image')
        self.send_docx_button = QPushButton('Send docx')

        vbox = QVBoxLayout()
        vbox.addWidget(self.message_history)

        hbox = QHBoxLayout()
        hbox.addWidget(self.message_input)
        hbox.addWidget(self.send_button)
        hbox.addWidget(self.send_file_button)
        hbox.addWidget(self.send_docx_button)

        vbox.addLayout(hbox)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.send_button.clicked.connect(self.send_message)
        self.send_file_button.clicked.connect(self.send_file)
        self.send_docx_button.clicked.connect(self.send_docx)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(('localhost', 9999))

        self.receive_thread = threading.Thread(target=self.handle_server)
        self.receive_thread.start()

    def handle_server(self):
        while True:
            try:
                ready_to_read, _, _ = select.select([self.server_socket], [], [], 0.1)
                if self.server_socket in ready_to_read:
                    data = self.server_socket.recv(1024)
                    if not data:
                        break
                    elif data.startswith(b'SIZE'):
                        filesize = int(data[5:])
                        filename = f"received_{int(time.time())}.docx"
                        with open(filename, 'wb') as f:
                            data = self.server_socket.recv(1024)
                            total_recv = len(data)
                            f.write(data)
                            while total_recv < filesize:
                                data = self.server_socket.recv(1024)
                                total_recv += len(data)
                                f.write(data)

                        self.message_history.append(f'File {filename} received')
                    else:
                        #self.message_history.setAlignment(Qt.AlignLeft)
                        message = data.decode('utf-8')
                        self.message_history.append(message.replace("\r", ""))
            except:
                break

        self.server_socket.close()
        sys.exit()

    def send_message(self):
        message = self.message_input.text()

        if message == 'q':
            self.server_socket.send(message.encode('utf-8'))
            self.server_socket.close()
            sys.exit()
        elif message:
            self.server_socket.send(message.encode('utf-8'))
            #self.message_history.setAlignment(Qt.AlignRight)
            #self.message_history.append(message)

        self.message_input.clear()

    def send_file(self):
        #filename = self.message_input.text()
        filename, _ = QFileDialog.getOpenFileName(self, 'Przeglądaj', '/', "Obrazy (*.png *.jpg *.jpeg)")
        #print(filename)
        if filename:
            try:
                img = Image.open(filename)

                ascii_art = convert_to_ascii_art(img)

                for line in ascii_art.strip().split('\n'):
                    if line:
                        self.server_socket.send(line.encode('utf-8'))
                        time.sleep(0.02)  # opóźnienie dla lepszej czytelności
            except:
                pass

        # Wyczyść pole tekstowe
        self.message_input.clear()

    def send_docx(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Przeglądaj', '/', "Pliki Word (*.docx)")
        if filename:
            try:
                filesize = os.path.getsize(filename)
                self.server_socket.send(f"SIZE {filesize}".encode('utf-8'))
                time.sleep(0.1)

                with open(filename, 'rb') as f:
                    data = f.read(1024)
                    while data:
                        self.server_socket.send(data)
                        data = f.read(1024)
                        time.sleep(0.02)  # opóźnienie dla lepszej czytelności

                print(f'File {filename} sent')
            except Exception as e:
                print(f"Error: {str(e)}")

        self.message_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont('consolas', 10)
    app.setFont(font)
    main_window = ChatWindow()
    main_window.show()

    sys.exit(app.exec_())
