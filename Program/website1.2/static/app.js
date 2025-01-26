// Глобальные переменные для данных частот и амплитуд
let frequenciesList = [];
let amplitudesList = [];

/**
 * Загрузка файлов на сервер
 */
async function uploadFiles() {
    console.log("Кнопка загрузки нажата.");
    const files = document.getElementById('files').files;

    if (files.length === 0) {
        alert("Выберите файл для загрузки!");
        return;
    }

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        // Отправка файлов на сервер
        const response = await fetch('/upload_files', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Ошибка загрузки файлов: ${response.statusText}`);
        }

        const result = await response.json();
        console.log("Ответ сервера:", result);

        // Сохраняем частоты и амплитуды в глобальные переменные
        if (result.frequencies && result.amplitudes) {
            frequenciesList = result.frequencies;
            amplitudesList = result.amplitudes;
            alert("Файлы успешно загружены!");
        } else {
            alert("Ошибка: Сервер не вернул данные частот и амплитуд.");
        }
    } catch (error) {
        console.error("Ошибка при загрузке файлов:", error);
        alert("Ошибка при загрузке файлов. Проверьте соединение с сервером.");
    }
}

/**
 * Обработка данных и построение графика
 */
async function processAndPlot() {
    console.log("Кнопка обработки нажата.");

    if (frequenciesList.length === 0 || amplitudesList.length === 0) {
        alert("Данные не загружены. Сначала загрузите файл.");
        return;
    }

    const params = {
        frequencies: frequenciesList,
        amplitudes: amplitudesList,
        remove_baseline: document.getElementById('remove_baseline').checked,
        apply_smoothing: document.getElementById('apply_smoothing').checked,
        normalize: document.getElementById('normalize').checked,
        find_peaks: document.getElementById('find_peaks').checked
    };

    try {
        // Отправка параметров обработки на сервер
        const response = await fetch('/process_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
        });

        if (!response.ok) {
            throw new Error(`Ошибка обработки данных: ${response.statusText}`);
        }

        const result = await response.json();
        console.log("Ответ от /process_data:", result);

        if (result.processed_amplitudes) {
            // Построение графика
            await plotSpectrum(params.frequencies, result.processed_amplitudes, result.peaks);
        } else {
            alert(`Ошибка обработки данных: ${result.error || "Неизвестная ошибка"}`);
        }
    } catch (error) {
        console.error("Ошибка в процессе обработки:", error);
        alert("Ошибка при обработке данных. Проверьте соединение с сервером.");
    }
}

/**
 * Построение графика с использованием Plotly
 */
async function plotSpectrum(frequencies, amplitudes, peaks = []) {
    try {
        const plotResponse = await fetch('/plot_spectrum', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frequencies, amplitudes, peaks }),
        });

        if (!plotResponse.ok) {
            throw new Error(`Ошибка построения графика: ${plotResponse.statusText}`);
        }

        const plotResult = await plotResponse.json();
        console.log("Ответ от /plot_spectrum:", plotResult);

        // Данные для построения графика
        const plotData = [
            {
                x: frequencies,
                y: amplitudes,
                type: 'scatter',
                mode: 'lines',
                name: 'Spectrum'
            },
            {
                x: peaks.map(i => frequencies[i]),
                y: peaks.map(i => amplitudes[i]),
                type: 'scatter',
                mode: 'markers',
                name: 'Peaks',
                marker: { color: 'red', size: 8 }
            }
        ];

        // Настройки графика
        const layout = {
            title: 'Спектр',
            xaxis: { title: 'Frequency' },
            yaxis: { title: 'Amplitude' },
            showlegend: true
        };

        // Отображение графика с помощью Plotly
        Plotly.newPlot('spectrum_plot', plotData, layout);
    } catch (error) {
        console.error("Ошибка при построении графика:", error);
        alert("Ошибка при построении графика.");
    }
}
