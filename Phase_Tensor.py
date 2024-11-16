import numpy as np
import matplotlib.pyplot as plt

def parse_edi_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = {
        'FREQ': [],
        'ZXXR': [],
        'ZXXI': [],
        'ZXYR': [],
        'ZXYI': [],
        'ZYXR': [],
        'ZYXI': [],
        'ZYYR': [],
        'ZYYI': []
    }

    reading_freq = False
    reading_zxxr = False
    reading_zyyi = False
    reading_zxxi = False
    reading_zxyr = False
    reading_zxyi = False
    reading_zyxr = False
    reading_zyxi = False
    reading_zyyr = False

    for line in lines:
        line = line.strip()

        if ">FREQ" in line:
            reading_freq = True
            continue
        elif ">ZXXR" in line:
            reading_freq = False
            reading_zxxr = True
            continue
        elif ">ZXXI" in line:
            reading_zxxr = False
            reading_zxxi = True
            continue
        elif ">ZXYR" in line:
            reading_zxxi = False
            reading_zxyr = True
            continue
        elif ">ZXYI" in line:
            reading_zxyr = False
            reading_zxyi = True
            continue
        elif ">ZYXR" in line:
            reading_zxyi = False
            reading_zyxr = True
            continue
        elif ">ZYXI" in line:
            reading_zyxr = False
            reading_zyxi = True
            continue
        elif ">ZYYR" in line:
            reading_zyxi = False
            reading_zyyr = True
            continue
        elif ">ZYYI" in line:
            reading_zyyr = False
            reading_zyyi = True
            continue

        if not line or any(char.isalpha() for char in line if char not in ('E', '+', '-', '.')):
            continue

        if reading_freq:
            data['FREQ'].extend([float(val) for val in line.split()])
        elif reading_zxxr:
            data['ZXXR'].extend([float(val) for val in line.split()])
        elif reading_zxxi:
            data['ZXXI'].extend([float(val) for val in line.split()])
        elif reading_zxyr:
            data['ZXYR'].extend([float(val) for val in line.split()])
        elif reading_zxyi:
            data['ZXYI'].extend([float(val) for val in line.split()])
        elif reading_zyxr:
            data['ZYXR'].extend([float(val) for val in line.split()])
        elif reading_zyxi:
            data['ZYXI'].extend([float(val) for val in line.split()])
        elif reading_zyyr:
            data['ZYYR'].extend([float(val) for val in line.split()])
        elif reading_zyyi:
            data['ZYYI'].extend([float(val) for val in line.split()])

    # Вывод содержимого и длины массивов
    for key, value in data.items():
        print(f"{key}: {value[:84]}")
        print(f"Length of {key}: {len(value)}")

    return data

def calculate_phase_tensor(data):
    # Получаем минимальную длину массивов
    min_length = min(len(data['ZXXR']), len(data['ZXXI']),
                     len(data['ZXYR']), len(data['ZXYI']),
                     len(data['ZYXR']), len(data['ZYXI']),
                     len(data['ZYYR']), len(data['ZYYI']))

    # Усечение массивов до минимального размера
    ReZxx = np.array(data['ZXXR'][:min_length])
    ImZxx = np.array(data['ZXXI'][:min_length])
    ReZxy = np.array(data['ZXYR'][:min_length])
    ImZxy = np.array(data['ZXYI'][:min_length])
    ReZyx = np.array(data['ZYXR'][:min_length])
    ImZyx = np.array(data['ZYXI'][:min_length])
    ReZyy = np.array(data['ZYYR'][:min_length])
    ImZyy = np.array(data['ZYYI'][:min_length])

    # Вычисление компонентов фазового тензора
    Φxx = (ReZyy * ImZxx - ReZxy * ImZyx) / (ReZxx * ReZyy - ReZxy * ReZyx)
    Φxy = (ReZyy * ImZxy - ReZxy * ImZyy) / (ReZxx * ReZyy - ReZxy * ReZyx)
    Φyx = (ReZxx * ImZyx - ReZyx * ImZxx) / (ReZxx * ReZyy - ReZxy * ReZyx)
    Φyy = (ReZxx * ImZyy - ReZyx * ImZxy) / (ReZxx * ReZyy - ReZxy * ReZyx)

    # Вычисление Φ1, Φ2, Φ3, Φ4 по формулам из книги
    Φ1 = (Φxy - Φyx) / 2
    Φ2 = (Φxx + Φyy) / 2
    Φ3 = (Φxy + Φyx) / 2
    Φ4 = (Φxx - Φyy) / 2

    # Вывод значений фазового тензора и Фи-компонентов
    print(f"Φxx: {Φxx}")
    print(f"Φxy: {Φxy}")
    print(f"Φyx: {Φyx}")
    print(f"Φyy: {Φyy}")
    print(f"Φ1: {Φ1}")
    print(f"Φ2: {Φ2}")
    print(f"Φ3: {Φ3}")
    print(f"Φ4: {Φ4}")

    return Φ1, Φ2, Φ3, Φ4

def plot_polar_diagram(Φ1, Φ2, Φ3, Φ4, title):
    alpha = np.linspace(0, 2 * np.pi, 360)  # Используем реальные данные, без интерполяции

    Φ1 = np.mean(Φ1)
    Φ2 = np.mean(Φ2)
    Φ3 = np.mean(Φ3)
    Φ4 = np.mean(Φ4)
    # Вычисление фазовых тензоров по формулам из книги
    Φxx_alpha = np.abs(np.arctan(Φ2 + Φ3 * np.sin(2 * alpha) + Φ4 * np.cos(2 * alpha)))
    Φxy_alpha = np.abs(np.arctan(Φ1 + Φ3 * np.cos(2 * alpha) - Φ4 * np.sin(2 * alpha)))

    # Построение диаграммы
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(alpha, Φxx_alpha, label='Φxx(α)')
    ax.plot(alpha, Φxy_alpha, label='Φxy(α)')
    ax.set_title(title)
    ax.legend()

    plt.show()

# Основная часть кода
edi_file_path = 'D:/0_Boom_2021/EDI/1.edi'
data = parse_edi_file(edi_file_path)
Φ1, Φ2, Φ3, Φ4 = calculate_phase_tensor(data)
plot_polar_diagram(Φ1, Φ2, Φ3, Φ4, 'Полярная диаграмма фазовых тензоров')
