import sympy as sp
import numpy as np


def integer_coordinates(func_str):
    """
    Возвращает отформатированные координаты, через которые проходит график функции,
    включая целые числа и числа, кратные 0.25.
    """
    x = sp.symbols('x')
    func = sp.sympify(func_str)
    f_lambdified = sp.lambdify(x, func, modules=['numpy'])

    coordinates = []

    for x_val in range(-5, 6):
        try:
            y_val = f_lambdified(x_val)
            y_rounded = round(y_val * 4) / 4  # Округляем значение до ближайшего числа, кратного 0.25
            if np.isclose(y_val, y_rounded, atol=1e-5):
                if y_rounded.is_integer():
                    coordinates.append((x_val, int(y_rounded)))
                else:
                    coordinates.append((x_val, y_rounded))
        except ZeroDivisionError:
            continue  # Пропускаем деление на ноль

    formatted_output = "Координаты точек:\n"
    for coord in coordinates:
        formatted_output += f"({coord[0]}, {coord[1]})\n"

    return formatted_output
