import os
from flask import Flask, request, jsonify, render_template
import matplotlib
matplotlib.use('Agg')  # Используем "безголовый" режим Matplotlib
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
    Загрузка файлов на сервер и извлечение данных частот и амплитуд.
    """
    if 'files' not in request.files:
        return jsonify({'error': 'Файлы не найдены'}), 400

    files = request.files.getlist('files')
    frequencies = []
    amplitudes = []

    try:
        for file in files:
            if file.filename == '':
                return jsonify({'error': 'Файл без имени'}), 400

            # Предполагаем, что файл - CSV с колонками frequency и amplitude, разделёнными пробелом
            content = file.read().decode('utf-8').splitlines()
            for line in content:
                freq, ampl = map(float, line.split())
                frequencies.append(freq)
                amplitudes.append(ampl)

        return jsonify({
            'message': 'Файлы успешно загружены',
            'files': [file.filename for file in files],
            'frequencies': frequencies,
            'amplitudes': amplitudes
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
        frequencies = np.array(data['frequencies'])
        amplitudes = np.array(data['amplitudes'])

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

        # Применение обработки
        if remove_baseline:
            baseline = baseline_als(amplitudes, lam, p)
            amplitudes -= baseline

        if apply_smoothing:
            amplitudes = smooth_signal(amplitudes, window_length, polyorder)

        if normalize:
            amplitudes = normalize_snv(amplitudes)

        peaks = []
        if find_peaks_flag:
            peaks = find_signal_peaks(amplitudes, width, prominence)

        return jsonify({
            'processed_amplitudes': amplitudes.tolist(),
            'peaks': peaks
        })
    except Exception as e:
        return jsonify({'error': f'Ошибка обработки данных: {str(e)}'}), 400

@app.route('/plot_spectrum', methods=['POST'])
def plot_spectrum():
    """
    Формирование данных для интерактивного графика (Plotly).
    """
    try:
        data = request.json
        frequencies = data['frequencies']
        amplitudes = data['amplitudes']
        peaks = data.get('peaks', [])

        plot_data = {
            'frequencies': frequencies,
            'amplitudes': amplitudes,
            'peaks_frequencies': [frequencies[i] for i in peaks],
            'peaks_amplitudes': [amplitudes[i] for i in peaks],
        }

        return jsonify(plot_data)

    except Exception as e:
        print("Ошибка при построении графика:", str(e))
        return jsonify({'error': f'Ошибка построения графика: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)
