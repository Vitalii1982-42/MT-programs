# Based on the assembly-like operations, I'm constructing a Python version
# that attempts to preserve the logical flow of data manipulations and conditions.

import os
import re
import pandas as pd
import numpy as np
from openpyxl import Workbook
import tkinter as tk
from tkinter import filedialog


def parse_edi_file(file_path):
    """
    Разбирает EDI-файл для извлечения необходимых параметров.
    """
    data = {
        "FREQ": [],
        "ZXXR": [], "ZXXI": [],
        "ZXYR": [], "ZXYI": [],
        "ZYXR": [], "ZYXI": [],
        "ZYYR": [], "ZYYI": [],
        "RHOXY": [], "RHOYX": [],
        "PHSXY": [], "PHSYX": [],
        "TXR": [], "TXI": [],
        "TYR": [], "TYI": []
    }

    with open(file_path, 'r') as file:
        lines = file.readlines()
        reading_freq = False
        reading_flag = None

        for line in lines:
            line = line.strip()
            print(f"Чтение строки: {line}")  # Отладочный вывод для проверки содержимого строки

            # Пропуск строк, содержащих нечисловые данные
            if "ROT=ZROT" in line or not re.search(r"\d", line):
                continue

            # Начало раздела с частотами (>FREQ)
            if line.startswith(">FREQ"):
                reading_freq = True
                reading_flag = "FREQ"
                continue

            # Начало раздела для различных компонент импеданса
            if line.startswith(">ZXXR"):
                reading_flag = "ZXXR"
                continue
            elif line.startswith(">ZXXI"):
                reading_flag = "ZXXI"
                continue
            elif line.startswith(">ZXYR"):
                reading_flag = "ZXYR"
                continue
            elif line.startswith(">ZXYI"):
                reading_flag = "ZXYI"
                continue
            elif line.startswith(">ZYXR"):
                reading_flag = "ZYXR"
                continue
            elif line.startswith(">ZYXI"):
                reading_flag = "ZYXI"
                continue
            elif line.startswith(">ZYYR"):
                reading_flag = "ZYYR"
                continue
            elif line.startswith(">ZYYI"):
                reading_flag = "ZYYI"
                continue
            elif line.startswith(">!**** APPARENT RESISTIVITIES AND PHASES****!"):
                reading_flag = "RHO_PHS"
                continue
            elif line.startswith(">!****TIPPER PARAMETERS****!"):
                reading_flag = "TIPPER"
                continue

            # Извлечение значений в зависимости от текущего флага
            if reading_flag == "FREQ" and re.match(r"[-+]?\d*\.\d+[eE][-+]?\d+|\d+", line):
                freq_values = re.findall(r"[-+]?\d*\.\d+[eE][-+]?\d+|\d+", line)
                data["FREQ"].extend([float(f) for f in freq_values])
            elif reading_flag in ["ZXXR", "ZXXI", "ZXYR", "ZXYI", "ZYXR", "ZYXI", "ZYYR", "ZYYI"]:
                data[reading_flag].extend(
                    [float(val) for val in line.split() if re.match(r"[-+]?\d*\.\d+([eE][-+]?\d+)?", val)])
            elif reading_flag == "RHO_PHS":
                rho_match = re.search(r"RHOXY\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if rho_match:
                    data["RHOXY"].append(float(rho_match.group(1)))
                rho_match = re.search(r"RHOYX\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if rho_match:
                    data["RHOYX"].append(float(rho_match.group(1)))
                phs_match = re.search(r"PHSXY\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if phs_match:
                    data["PHSXY"].append(float(phs_match.group(1)))
                phs_match = re.search(r"PHSYX\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if phs_match:
                    data["PHSYX"].append(float(phs_match.group(1)))
            elif reading_flag == "TIPPER":
                txr_match = re.search(r"TXR\.EXP\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if txr_match:
                    data["TXR"].append(float(txr_match.group(1)))
                txi_match = re.search(r"TXI\.EXP\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if txi_match:
                    data["TXI"].append(float(txi_match.group(1)))
                tyr_match = re.search(r"TYR\.EXP\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if tyr_match:
                    data["TYR"].append(float(tyr_match.group(1)))
                tyi_match = re.search(r"TYI\.EXP\s*=\s*([-+]?\d*\.\d+[eE][-+]?\d+)", line)
                if tyi_match:
                    data["TYI"].append(float(tyi_match.group(1)))

    # Дополнение массивов до одинаковой длины
    max_length = max(len(values) for values in data.values())
    for key in data:
        if len(data[key]) < max_length:
            data[key].extend([None] * (max_length - len(data[key])))

    # Отладочный вывод для проверки извлеченных данных
    print("Извлеченные данные для частот:", data["FREQ"])
    print("Извлеченные данные для ZXYR:", data["ZXYR"])

    return data


def create_xlsx_from_edi_folder(folder_path, output_file_path):
    """
    Создает XLSX файл из EDI-файлов в указанной папке, объединяя данные в один лист.
    """
    all_data = []
    edi_files = [f for f in os.listdir(folder_path) if f.endswith('.edi')]

    for idx, edi_file in enumerate(edi_files):
        file_path = os.path.join(folder_path, edi_file)
        print(f"Обработка файла: {file_path}")
        edi_data = parse_edi_file(file_path)
        if not edi_data["FREQ"]:
            print(f"Файл {edi_file} не содержит данных о частоте.")
            continue
        df = pd.DataFrame(edi_data)

        # Проверка на наличие нулевых частот и их обработка
        if (df['FREQ'] == 0).any():
            print(f"Обнаружены нулевые значения частот в файле {edi_file}.")

        # Вычисление периода и логарифма периода
        df['Period'] = 1 / df['FREQ']
        df['LogPeriod'] = np.log10(df['Period'])

        # Добавление данных в общий список
        for _, row in df.iterrows():
            all_data.append([
                idx + 1,  # Индекс файла
                row['FREQ'],  # Частота
                row['Period'],  # Период
                row['LogPeriod'],  # Логарифм периода
                row.get('ZXXR', None), row.get('ZXXI', None),
                row.get('ZXYR', None), row.get('ZXYI', None),
                row.get('ZYXR', None), row.get('ZYXI', None),
                row.get('ZYYR', None), row.get('ZYYI', None),
                row.get('RHOXY', None), row.get('RHOYX', None),
                row.get('PHSXY', None), row.get('PHSYX', None),
                row.get('TXR', None), row.get('TXI', None),
                row.get('TYR', None), row.get('TYI', None)
            ])

    if not all_data:
        print("Нет данных для записи в выходной файл.")
        return

    # Создание выходной рабочей книги
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Объединенные данные"

    # Запись заголовков
    headers = [
        "Индекс", "Частота (Гц)", "Период (с)", "Логарифм периода", "ZXXR", "ZXXI", "ZXYR", "ZXYI", "ZYXR", "ZYXI",
        "ZYYR", "ZYYI", "RHOXY", "RHOYX", "PHSXY", "PHSYX", "TXR", "TXI", "TYR", "TYI"
    ]
    sheet.append(headers)

    # Запись строк данных
    for data_row in all_data:
        sheet.append(data_row)

    # Сохранение рабочей книги по указанному пути
    workbook.save(output_file_path)
    print(f"XLSX файл сохранен как: {output_file_path}")


# Пример использования
root = tk.Tk()
root.withdraw()  # Скрыть основное окно Tkinter

# Выбор папки с EDI-файлами
edi_folder_path = filedialog.askdirectory(title="Выберите папку с EDI-файлами")
if not edi_folder_path:
    print("Папка с EDI-файлами не выбрана. Завершение работы.")
else:
    output_xlsx_path = filedialog.asksaveasfilename(defaultextension=".xlsx", title="Сохранить файл как",
                                                    filetypes=[("Excel файлы", "*.xlsx")])
    if not output_xlsx_path:
        print("Выходной файл не выбран. Завершение работы.")
    else:
        # Создание XLSX файла из папки с EDI-файлами
        create_xlsx_from_edi_folder(edi_folder_path, output_xlsx_path)