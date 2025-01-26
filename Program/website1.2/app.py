import os
from flask import Flask, request, jsonify, render_template
import numpy as np
from data_processing import baseline_als, smooth_signal, normalize_snv, find_signal_peaks

# Инициализация приложения Flask
app = Flask(__name__)

# Директория для сохранения загруженных файлов
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """
    Отображение главной страницы.
    """
    return render_template('index.html')

@app.route('/upload_files', methods=['POST'])
def upload_files():
    """
    Загрузка нескольких файлов на сервер и извлечение данных частот и амплитуд для каждого файла.
    """
    if 'files' not in request.files:
        return jsonify({'error': 'Файлы не найдены'}), 400

    files = request.files.getlist('files')
    all_frequencies = []
    all_amplitudes = []
    file_names = []

    try:
        for file in files:
            if file.filename == '':
                return jsonify({'error': 'Один из файлов не имеет имени'}), 400

            # Читаем данные из файла
            content = file.read().decode('utf-8').splitlines()
            frequencies = []
            amplitudes = []

            for line in content:
                try:
                    freq, ampl = map(float, line.split())
                    frequencies.append(freq)
                    amplitudes.append(ampl)
                except ValueError:
                    return jsonify({'error': f'Неверный формат данных в файле {file.filename}'}), 400

            # Сохраняем данные для каждого файла
            all_frequencies.append(frequencies)
            all_amplitudes.append(amplitudes)
            file_names.append(file.filename)

        return jsonify({
            'message': 'Файлы успешно загружены',
            'files': file_names,
            'frequencies': all_frequencies,
            'amplitudes': all_amplitudes
        })

    except Exception as e:
        return jsonify({'error': f'Ошибка обработки файлов: {str(e)}'}), 400

@app.route('/process_data', methods=['POST'])
def process_data():
    """
    Обработка данных: удаление базовой линии, сглаживание, нормализация, поиск пиков.
    """
    try:
        data = request.json
        all_frequencies = data.get('frequencies', [])
        all_amplitudes = data.get('amplitudes', [])

        if not all_frequencies or not all_amplitudes:
            raise ValueError("Данные частот или амплитуд отсутствуют или некорректны.")

        # Параметры обработки
        lam = data.get('lam', 1000)
        p = data.get('p', 0.001)
        window_length = data.get('window_length', 25)
        polyorder = data.get('polyorder', 2)
        width = data.get('width', 1)
        prominence = data.get('prominence', 1)
        remove_baseline = data.get('remove_baseline', False)
        apply_smoothing = data.get('apply_smoothing', False)
        normalize = data.get('normalize', False)
        find_peaks_flag = data.get('find_peaks', False)

        processed_amplitudes = []
        peaks_list = []
        peaks_values_list = []

        for frequencies, amplitudes in zip(all_frequencies, all_amplitudes):
            amplitudes = np.array(amplitudes)  # Преобразуем в numpy.ndarray

            if amplitudes.size == 0:
                raise ValueError("Массив амплитуд пустой.")

            if remove_baseline:
                baseline = baseline_als(amplitudes, lam, p)
                amplitudes -= baseline

            if apply_smoothing:
                if amplitudes.size < window_length:
                    raise ValueError("Длина сигнала меньше размера окна сглаживания.")
                amplitudes = smooth_signal(amplitudes, window_length, polyorder)

            if normalize:
                amplitudes = normalize_snv(amplitudes)

            peaks = []
            peaks_values = []
            if find_peaks_flag:
                peaks, _ = find_signal_peaks(amplitudes, width=width, prominence=prominence)
                peaks_values = amplitudes[peaks] if peaks.size > 0 else []

            processed_amplitudes.append(amplitudes.tolist())
            peaks_list.append(peaks.tolist() if len(peaks) > 0 else [])
            peaks_values_list.append(peaks_values.tolist() if len(peaks_values) > 0 else [])

        return jsonify({
            'processed_amplitudes': processed_amplitudes,
            'peaks': peaks_list,
            'peaks_values': peaks_values_list
        })

    except Exception as e:
        print("Ошибка обработки данных:", str(e))
        return jsonify({'error': f'Ошибка обработки данных: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)
