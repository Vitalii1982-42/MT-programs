import os
import re
import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, simpledialog


def parse_edi_file(file_path):
    """
    Парсинг данных из EDI-файла и извлечение нужных данных.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = {
        'FR': [],
        'ZXXR': [],
        'ZXXI': [],
        'ZXYR': [],
        'ZXYI': [],
        'ZYXR': [],
        'ZYXI': [],
        'ZYYR': [],
        'ZYYI': [],
        'RHOXY': [],
        'RHOYX': [],
        'PHSXY': [],
        'PHSYX': [],
        'TXR': [],
        'TXI': [],
        'TYR': [],
        'TYI': []
    }

    reading_section = None
    freq_count = 0

    for line in lines:
        line = line.strip()

        if 'NFREQ=' in line:
            match = re.search(r'NFREQ=(\d+)', line)
            if match:
                freq_count = int(match.group(1))

        if '>FREQ' in line:
            reading_section = 'FR'
            continue
        elif '>ZXXR' in line:
            reading_section = 'ZXXR'
            continue
        elif '>ZXXI' in line:
            reading_section = 'ZXXI'
            continue
        elif '>ZXYR' in line:
            reading_section = 'ZXYR'
            continue
        elif '>ZXYI' in line:
            reading_section = 'ZXYI'
            continue
        elif '>ZYXR' in line:
            reading_section = 'ZYXR'
            continue
        elif '>ZYXI' in line:
            reading_section = 'ZYXI'
            continue
        elif '>ZYYR' in line:
            reading_section = 'ZYYR'
            continue
        elif '>ZYYI' in line:
            reading_section = 'ZYYI'
            continue
        elif '>RHOXY' in line:
            reading_section = 'RHOXY'
            continue
        elif '>RHOYX' in line:
            reading_section = 'RHOYX'
            continue
        elif '>PHSXY' in line:
            reading_section = 'PHSXY'
            continue
        elif '>PHSYX' in line:
            reading_section = 'PHSYX'
            continue
        elif '>TXR' in line:
            reading_section = 'TXR'
            continue
        elif '>TXI' in line:
            reading_section = 'TXI'
            continue
        elif '>TYR' in line:
            reading_section = 'TYR'
            continue
        elif '>TYI' in line:
            reading_section = 'TYI'
            continue

        if not line or any(char.isalpha() for char in line if char not in ('E', '+', '-', '.')):
            continue

        if reading_section == 'FR' and freq_count > 0:
            data['FR'].extend([float(val) for val in line.split()])
            freq_count -= len(line.split())
            if freq_count <= 0:
                reading_section = None
        elif reading_section and reading_section != 'FR':
            data[reading_section].extend([float(val) for val in line.split()])

    # Проверка на соответствие количества частот и значений компонент
    frequencies = data['FR']
    for component in data:
        if component != 'FR':
            if len(data[component]) < len(frequencies):
                print(f"Предупреждение: количество значений {component} меньше количества частот. Заполняем NaN.")
                data[component].extend([np.nan] * (len(frequencies) - len(data[component])))
            elif len(data[component]) > len(frequencies):
                print(f"Предупреждение: количество значений {component} больше количества частот. Обрезаем лишние значения.")
                data[component] = data[component][:len(frequencies)]

    return data


def process_folder(folder_path):
    """
    Считывание всех EDI-файлов в папке и их обработка.
    """
    all_data = []
    file_counter = 1

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.edi'):
                file_path = os.path.join(root, file_name)
                file_data = parse_edi_file(file_path)
                df = pd.DataFrame(file_data)
                df.insert(0, 'file_number', file_counter)
                all_data.append(df)
                file_counter += 1

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def save_to_xlsx(df, output_file):
    """
    Сохранение данных в XLSX файл.
    """
    df.to_excel(output_file, index=False)


if __name__ == "__main__":
    # Диалог для выбора папки с EDI-файлами
    root = Tk()
    root.withdraw()  # Скрыть главное окно
    folder_path = filedialog.askdirectory(title="Выберите папку с EDI-файлами")

    if folder_path:
        try:
            # Считывание и обработка EDI-файлов
            df = process_folder(folder_path)

            # Добавление столбцов с периодами и логарифмом периода
            if not df.empty:
                df.insert(2, 'Per', 1 / df['FR'])
                df.insert(3, 'LgPer', np.log10(df['Per']))

                # Диалог для ввода минимальной и максимальной частоты
                min_freq = df['FR'].min()
                max_freq = df['FR'].max()
                min_freq_input = simpledialog.askfloat("Минимальная частота",
                                                       f"Введите минимальную частоту (доступный диапазон: {min_freq} - {max_freq})",
                                                       initialvalue=min_freq)
                max_freq_input = simpledialog.askfloat("Максимальная частота",
                                                       f"Введите максимальную частоту (доступный диапазон: {min_freq} - {max_freq})",
                                                       initialvalue=max_freq)

                # Фильтрация данных по диапазону частот
                if min_freq_input is not None and max_freq_input is not None:
                    df = df[(df['FR'] >= min_freq_input) & (df['FR'] <= max_freq_input)]

                # Диалог для выбора пути сохранения XLSX-файла
                output_file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                           filetypes=[("Excel files", "*.xlsx")],
                                                           title="Сохранить файл как")
                if output_file:
                    save_to_xlsx(df, output_file)
                    print(f"Данные успешно сохранены в файл {output_file}")
                else:
                    print("Сохранение файла отменено.")
            else:
                print("Не удалось найти данные для сохранения.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    else:
        print("Папка не была выбрана.")