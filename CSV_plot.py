import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных из CSV-файла
data = pd.read_csv('D:\\0_Boom\\1\\1571925b1.csv')

# Корректировка столбца Time: вычитаем первое значение
data['Time'] = data['Time'] - data['Time'].iloc[0]

# Проверяем, что данные загружены корректно
print(data.head())

# Получение названий столбцов (предположим, они уже есть в файле)
columns = data.columns
print("Названия столбцов:", columns)

# Определение столбцов для построения графиков
x_col = 'Time'  # Столбец 1 (время)
y_cols = ['Ex', 'Ey', 'Hz', 'Hy', 'Hz']  # Столбцы 2-6

# Создаем словари для настраиваемых подписей осей
x_labels = {
    x_col: "Время (с)"  # Настраиваемая подпись для оси X (время)
}

y_labels = {
    'Ex': "Электрическое поле Ex (В/м)",
    'Ey': "Электрическое поле Ey (В/м)",
    'Hz': "Магнитное поле Hz (А/м)",
    'Hy': "Магнитное поле Hy (А/м)"
}

# Создаем фигуру для графиков
plt.figure(figsize=(14, 12))  # Размер фигуры

# Построим графики зависимости столбцов 2-6 от столбца 1
for i, col in enumerate(y_cols, 1):
    plt.subplot(3, 2, i)  # Создаем подграфики 3х2 (6 графиков)
    plt.plot(data[x_col], data[col], marker='o', linestyle='-')

    # Получаем названия осей
    x_label = x_labels.get(x_col, x_col)
    y_label = y_labels.get(col, col)

    # Настраиваем подписи и заголовки
#    plt.title(f' {y_label} от {x_label}')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)

# Оптимизируем расположение графиков
plt.tight_layout()

# Показать все графики
plt.show()
