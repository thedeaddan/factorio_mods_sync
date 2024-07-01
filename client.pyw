import os
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from pathlib import Path

# Получение имени пользователя системы
USER_NAME = os.getlogin()
CLIENT_DIRECTORY = Path(f'C:/Users/{USER_NAME}/AppData/Roaming/Factorio/mods')

SERVER_URL = 'http://192.168.1.48:5000'  # Убедитесь, что IP-адрес сервера правильный

def get_server_files():
    response = requests.get(f'{SERVER_URL}/files')
    if response.status_code == 200:
        return response.json()
    else:
        return []

def download_file(filename, progress_callback):
    url = f'{SERVER_URL}/files/{filename}'
    response = requests.get(url)
    if response.status_code == 200:
        file_path = CLIENT_DIRECTORY / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Создание родительских директорий
        with open(file_path, 'wb') as f:
            f.write(response.content)
        progress_callback(filename, True)
    else:
        progress_callback(filename, False)

def get_client_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            file_list.append(relative_path)
    return file_list

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Sync Client')
        self.syncing = False
        
        self.label = ttk.Label(root, text='File Sync Client', font=('Helvetica', 16), foreground='white', background='black')
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.file_list = tk.Listbox(root, width=60, height=15, bg='black', fg='white')
        self.file_list.pack(pady=10)

        self.sync_button = ttk.Button(root, text='Start Sync', command=self.start_sync)
        self.sync_button.pack(pady=10)

        self.stop_button = ttk.Button(root, text='Stop Sync', command=self.stop_sync, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
    def update_progress(self, filename, success):
        if filename:
            status = 'Downloaded' if success else 'Failed'
            self.file_list.insert(tk.END, f'{filename} - {status}')
            self.root.update_idletasks()
        else:
            self.label.config(text='Sync Complete')
            self.progress.stop()
            self.syncing = False
            self.sync_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def start_sync(self):
        self.label.config(text='Syncing Files...')
        self.file_list.delete(0, tk.END)
        self.progress.start()
        self.sync_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.syncing = True
        threading.Thread(target=self.sync_files).start()

    def stop_sync(self):
        self.syncing = False
        self.label.config(text='Sync Stopped')
        self.sync_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def sync_files(self):
        server_files = get_server_files()
        client_files = get_client_files(CLIENT_DIRECTORY)
        
        for file in server_files:
            if not self.syncing:
                break
            if file not in client_files:
                download_file(file, self.update_progress)
        self.update_progress(None, None)  # Signal completion

if __name__ == '__main__':
    if not os.path.exists(CLIENT_DIRECTORY):
        os.makedirs(CLIENT_DIRECTORY)

    root = ThemedTk(theme='black')
    app = ClientApp(root)
    root.configure(bg='black')
    root.mainloop()
