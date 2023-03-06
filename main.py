import os
import subprocess
import sys
import atexit
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QPushButton, QGroupBox
from threading import Thread

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        env_path = os.path.abspath('./venv')
        site_packages_path = os.path.join(env_path, 'Lib', 'site-packages')  # Dla systemu Windows
        # site_packages_path = os.path.join(env_path, 'lib', 'python3.9', 'site-packages')  # Dla systemów Linux lub MacOS
        os.environ['PYTHONPATH'] = site_packages_path

        layout = QVBoxLayout()

        group_box = QGroupBox()
        group_box_layout = QHBoxLayout()
        group_box.setLayout(group_box_layout)
        group_box.setTitle('Liczba klientów')

        self.num_clients = 1
        for i in range(1, 6):
            radio_button = QRadioButton(str(i))
            radio_button.setChecked(i == 1)
            radio_button.clicked.connect(self.set_num_clients)
            group_box_layout.addWidget(radio_button)

        layout.addWidget(group_box)

        start_button = QPushButton('Start')
        start_button.clicked.connect(self.start_server_and_clients)
        layout.addWidget(start_button)

        self.setLayout(layout)
        self.setWindowTitle('Client-Server')

    def set_num_clients(self):
        sender = self.sender()
        self.num_clients = int(sender.text())

    def start_server_and_clients(self):
        self.server_process = subprocess.Popen(['python', 'server.py'])
        self.client_processes = []
        for i in range(self.num_clients):
            client_process = subprocess.Popen(['python', 'client.py'])
            self.client_processes.append(client_process)

        # Zarejestrowanie funkcji, która zostanie wywołana przy zakończeniu działania programu
        atexit.register(self.close_processes)

    def close_processes(self):
        self.server_process.terminate()
        for client_process in self.client_processes:
            client_process.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
