import socket
import numpy as np
from tkinter import filedialog, Tk
import matplotlib.pyplot as plt


def load_data():
    root = Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if not filepath:
        print("Файл не выбран.")
        return None, None
    data = np.genfromtxt(filepath, skip_header=1)
    frequencies = data[:, 0]
    amplitudes = data[:, 1]
    return frequencies, amplitudes


def format_data(frequencies, amplitudes):
    return "*".join(f"{f}|{a}" for f, a in zip(frequencies, amplitudes))


def parse_data(data):
    frequencies, amplitudes = [], []
    spectra = data.split("*")
    for point in spectra:
        freq, ampl = map(float, point.split("|"))
        frequencies.append(freq)
        amplitudes.append(ampl)
    return np.array(frequencies), np.array(amplitudes)


def visualize_data(frequencies, amplitudes):
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, amplitudes, label="Обработанный спектр", color="blue")
    plt.xlabel("Частота (см⁻¹)")
    plt.ylabel("Интенсивность")
    plt.title("Результат обработки спектра")
    plt.grid(True)
    plt.legend()
    plt.show()


def main():
    HOST = "127.0.0.1"
    PORT = 8000

    
    frequencies, amplitudes = load_data()
    if frequencies is None or amplitudes is None:
        return

    
    data_to_send = format_data(frequencies, amplitudes)

    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("Подключение к серверу установлено.")
        client_socket.sendall(data_to_send.encode())
        print("Данные отправлены на сервер.")
        
        
        response = client_socket.recv(10000).decode()
        print("Данные получены от сервера.")
        
        
        processed_frequencies, processed_amplitudes = parse_data(response)
        
        
        visualize_data(processed_frequencies, processed_amplitudes)

if __name__ == "__main__":
    main()
