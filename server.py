import socket
import numpy as np
from scipy.signal import savgol_filter
from scipy.sparse.linalg import spsolve
from scipy import sparse


def baseline_als(amplitudes, lam, p, niter=10):
    L = len(amplitudes)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + float(lam) * D.dot(D.transpose())
        z = spsolve(Z, w * amplitudes)
        w = p * (amplitudes > z) + (1 - p) * (amplitudes < z)
    return z

def delete_baseline(amplitudes, lam, p):
    baseline = baseline_als(amplitudes, lam, p)
    return amplitudes - baseline

def savgol_def(spectrum, window_length, polyorder):
    return savgol_filter(spectrum, window_length, polyorder)


def parse_data(data):
    frequencies, amplitudes = [], []
    spectra = data.split("*")
    for point in spectra:
        if "|" in point:  
            try:
                freq, ampl = map(float, point.split("|"))
                frequencies.append(freq)
                amplitudes.append(ampl)
            except ValueError:
                print(f"Ошибка обработки точки: {point}")
    return np.array(frequencies), np.array(amplitudes)



def format_data(frequencies, amplitudes):
    return "*".join(f"{f}|{a}" for f, a in zip(frequencies, amplitudes))


def main():
    HOST = "127.0.0.1"
    PORT = 8000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Сервер запущен и ждет подключения клиента...")
        
        conn, addr = server_socket.accept()
        with conn:
            print(f"Подключен клиент: {addr}")
            
            
            data = conn.recv(10000).decode()
            print("Данные получены от клиента.")
            
           
            frequencies, amplitudes = parse_data(data)
            
            
            lam, p = 1000, 0.001
            amplitudes = delete_baseline(amplitudes, lam, p)
            amplitudes = savgol_def(amplitudes, window_length=25, polyorder=2)

            
            response = format_data(frequencies, amplitudes)
            conn.sendall(response.encode())
            print("Обработанные данные отправлены клиенту.")

if __name__ == "__main__":
    main()
