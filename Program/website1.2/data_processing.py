import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.sparse.linalg import spsolve
from scipy import sparse

def baseline_als(amplitudes, lam=1000, p=0.001, niter=10):
    """
    Удаление базовой линии методом ALS.
    """
    if not isinstance(amplitudes, np.ndarray):
        amplitudes = np.array(amplitudes)

    if amplitudes.size == 0:
        raise ValueError("Массив амплитуд пустой.")

    L = len(amplitudes)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w * amplitudes)
        w = p * (amplitudes > z) + (1 - p) * (amplitudes < z)
    return z

def smooth_signal(amplitudes, window_length=25, polyorder=2):
    """
    Сглаживание сигнала методом Савицкого-Голая.
    """
    if not isinstance(amplitudes, np.ndarray):
        amplitudes = np.array(amplitudes)

    if len(amplitudes) < window_length:
        raise ValueError("Длина сигнала меньше размера окна сглаживания.")
    return savgol_filter(amplitudes, window_length, polyorder)

def normalize_snv(amplitudes):
    """
    Нормализация методом SNV (Standard Normal Variate).
    """
    if not isinstance(amplitudes, np.ndarray):
        amplitudes = np.array(amplitudes)

    if amplitudes.size == 0:
        raise ValueError("Массив амплитуд пустой.")

    mean = np.mean(amplitudes)
    std = np.std(amplitudes)
    if std == 0:
        raise ValueError("Стандартное отклонение равно нулю. Нормализация невозможна.")
    return (amplitudes - mean) / std

def find_signal_peaks(amplitudes, width=1, prominence=1):
    """
    Поиск пиков в сигнале.
    """
    if not isinstance(amplitudes, np.ndarray):
        amplitudes = np.array(amplitudes)

    if amplitudes.size == 0:
        raise ValueError("Массив амплитуд пустой.")

    peaks, properties = find_peaks(amplitudes, width=width, prominence=prominence)
    return peaks, properties

