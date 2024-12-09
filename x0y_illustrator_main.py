import sys
import matplotlib
import os
import numpy as np
import sympy as sp
from analiz import get_function_characteristics  # Импорт функции для анализа характеристик функции
from intervals_of_monotonicity import analyze_and_translate_function  # Для анализа монотонности функции
from int_numbers import integer_coordinates  # Для получения целочисленных координат
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QRadioButton, QDialog, QTableWidget, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as ToolBar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from database_utils import save_function_to_history, load_history, delete_history  # Импортируем функции для работы с БД
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QIcon  # Для анимации GIF

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvas):  # Класс для канваса, на котором будут отображаться графики
    def __init__(self, fig):
        self.fig = fig
        super().__init__(self.fig)  # Инициализация родительского класса
        self.updateGeometry()

class HistoryWindow(QDialog):  # Окно истории для отображения ранее построенных графиков
    def __init__(self):
        super().__init__()
        self.setWindowTitle('История построенных графиков')
        self.setGeometry(200, 200, 230, 300)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)  # Количество столбцов в таблице
        self.tableWidget.setHorizontalHeaderLabels(['Функция', 'Время'])  # Заголовки таблицы

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)  # Добавляем таблицу в окно
        self.setLayout(layout)

        self.load_history()  # Загружаем историю

    def load_history(self):  # Функция для загрузки истории построенных графиков
        data = load_history()  # Получаем данные из БД
        self.tableWidget.setRowCount(len(data))  # Устанавливаем количество строк в таблице
        for row_number, row_data in enumerate(data):
            self.tableWidget.insertRow(row_number)  # Вставляем строку
            for column_number, data_item in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data_item)))  # Вставляем данные в ячейку

        self.tableWidget.resizeColumnsToContents()  # Автоматически настраиваем размер столбцов

class AnalysisThread(QThread):  # Поток для выполнения анализа функции
    analysis_finished = pyqtSignal(str)  # Сигнал завершения анализа
    analysis_failed = pyqtSignal(str)  # Сигнал ошибки анализа

    def __init__(self, func_str):
        super().__init__()
        self.func_str = func_str  # Строка с функцией

    def run(self):
        try:
            # Анализируем характеристики функции, монотонность и целочисленные координаты
            characteristics = get_function_characteristics(self.func_str)
            monotonic_intervals = analyze_and_translate_function(self.func_str)
            integer_coords = integer_coordinates(self.func_str)

            result = 'Функция: {}\n\n'.format(self.func_str)
            for key, value in characteristics.items():
                result += f'{key}: {value}\n\n'
            result += 'Промежутки монотонности:\n'
            result += monotonic_intervals.get('Промежутки монотонности', 'Нет данных')
            result += '\n\n'
            result += integer_coords

            self.analysis_finished.emit(result)  # Отправляем результат в основной поток
        except Exception as e:
            self.analysis_failed.emit(str(e))  # Отправляем ошибку, если что-то пошло не так

def parse_function(func_str):  # Преобразуем строку с функцией, заменяя '^' на '**' и '|' на 'abs()'
    func_str = func_str.replace('^', '**')  # Заменяем возведение в степень

    return func_str

class X0yIllustrator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.png'))
        self.history_window = None
        self.analysis_thread = None
        self.derivative_plot = None
        self.y = None
        self.x = None
        self.func_for_base = None
        # Определяем путь к файлу UI в зависимости от окружения
        if hasattr(sys, '_MEIPASS'):
            ui_file_path = os.path.join(sys._MEIPASS, 'x0y illustrator.ui')
        else:
            ui_file_path = 'x0y illustrator.ui'

        # Загружаем UI
        uic.loadUi(ui_file_path, self)
        # Загружаем интерфейс из .ui файла
        self.setWindowTitle('x0y Illustrator')

        # Настройка шрифта для поля ввода
        font = self.task_field.font()
        font.setPointSize(14)
        self.task_field.setFont(font)

        self.setFixedSize(self.size())  # Фиксируем размер окна

        self.fig = Figure()  # Создаем фигуру для графика
        self.canvas = MplCanvas(self.fig)  # Канвас для отображения графика
        self.layout = QVBoxLayout(self.widget)
        self.toolbar = ToolBar(self.canvas, self)  # Панель инструментов
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.ani = None
        self.line = None

        # Радио-кнопки для выбора анимации
        self.radio_with_animation = QRadioButton('С анимацией', self)
        self.radio_without_animation = QRadioButton('Без анимацией', self)
        self.radio_with_animation.setChecked(True)
        self.layout.addWidget(self.radio_with_animation)
        self.layout.addWidget(self.radio_without_animation)

        # Настройка шрифта для радио-кнопок
        font = self.radio_with_animation.font()
        font.setPointSize(14)
        self.radio_with_animation.setFont(font)
        self.radio_without_animation.setFont(font)

        # Настройка шрифта для таблицы анализа
        font = self.Analiz_table.font()
        font.setPointSize(14)
        self.Analiz_table.setFont(font)

        self.loading_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем GIF

        # Подключаем кнопки к функциям
        self.History_button.clicked.connect(self.open_history_window)
        self.solve_button.clicked.connect(self.plot)
        self.derivative_button.clicked.connect(self.plot_derivative)
        self.History_delete.clicked.connect(self.clear_history)

    def plot(self):
        try:
            self.error_label.clear()  # Очищаем ошибки
            self.clear_canvas()  # Очищаем канвас
            self.Analiz_table.clear()  # Очищаем таблицу анализа
            self.func_for_base = self.task_field.toPlainText()  # Получаем строку с функцией
            func_str = parse_function(self.func_for_base)  # Преобразуем строку функции

            try:
                self.x = np.linspace(-100, 100, 550)  # Создаем массив X для графика
                x_sym = sp.symbols('x')  # Символ для переменной x
                func = sp.sympify(func_str)  # Преобразуем строку в символьную функцию
                f_lambdified = sp.lambdify(x_sym, func, modules=['numpy'])  # Лямбда-функция для вычислений
                self.y = f_lambdified(self.x)  # Вычисляем Y по функции
                self.y = np.array(self.y, dtype=np.float64)  # гарантируем float64 массив
                self.y[np.isnan(self.y) | np.isinf(self.y) | (np.abs(self.y) > 1e5)] = np.nan

                # Создаем график
                ax = self.fig.add_subplot(111)
                ax.set_xlabel(r'$y$', fontsize=16)
                ax.set_ylabel(r'$x$', fontsize=16)
                ax.set_xlim(min(self.x), max(self.x))
                ax.set_ylim(min(self.y), max(self.y))
                ax.relim()
                ax.autoscale_view()
                ax.minorticks_on()
                ax.grid(which='major')
                ax.grid(which='minor', linestyle=':')
                ax.set_title(fr'График функции: ${self.func_for_base}$')

                ax.axhline(0, color='black', linewidth=1.5)  # Ось y = 0 (горизонтальная линия)
                ax.axvline(0, color='black', linewidth=1.5)  # Ось x = 0 (вертикальная линия)

                # Выбираем анимацию или обычный график
                if self.radio_with_animation.isChecked():
                    self.animate_graph(ax)
                else:
                    ax.plot(self.x, self.y, label=fr'Функция: ${self.func_for_base}$')
                    ax.legend()

                self.fig.tight_layout()  # Автоматически подгоняем размер графика
                self.canvas.draw()  # Отображаем график
                save_function_to_history(self.func_for_base)  # Сохраняем функцию в историю

                self.start_analysis()  # Начинаем анализ функции
            except ValueError:
                ax.clear()
                self.error_label.setText('Не верный запрос, попробуйте так x^2')
                self.canvas.draw()
        except Exception:
            self.error_label.setText('Пожалуйста введите запрос, например 1/x')

    def clear_canvas(self):
        if self.ani:
            try:
                self.ani.event_source.stop()  # Останавливаем анимацию, если она есть
            except Exception:
                pass
            self.ani = None
        self.fig.clear()  # Очищаем график
        self.canvas.draw()

    def plot_derivative(self):
        if not hasattr(self, 'func_for_base') or not self.func_for_base:
            return

        try:
            # Если график производной существует, удаляем его
            if hasattr(self, 'derivative_plot') and self.derivative_plot is not None:
                self.derivative_plot.remove()  # Удаляем старую линию
                self.derivative_plot = None  # Сбрасываем флаг

            # Строим производную функции
            x_sym = sp.symbols('x')
            func = sp.sympify(self.func_for_base)
            derivative = sp.diff(func, x_sym)  # Вычисляем производную
            f_lambdified_deriv = sp.lambdify(x_sym, derivative, modules=['numpy'])
            y_derivative = f_lambdified_deriv(self.x)

            # Добавляем график производной на уже существующую ось
            ax = self.canvas.fig.axes[0]
            self.derivative_plot, = ax.plot(self.x, y_derivative, label=f'Производная: ${sp.latex(derivative)}$',
                                            color='red')
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            self.error_label.setText(fr'У графика {self.func_for_base} нет производной: {e}')

    def animate_graph(self, ax):
        self.line, = ax.plot([], [], label=fr'Функция: ${self.func_for_base}$')
        ax.legend()

        def init():
            self.line.set_data([], [])  # Инициализация графика
            return self.line,

        def update(frame):
            step = 2
            self.line.set_data(self.x[:frame * step], self.y[:frame * step])  # Обновление данных для анимации
            return self.line,

        interval = 16
        frames = len(self.x) // 2

        self.ani = FuncAnimation(self.fig, update, frames=frames, init_func=init, interval=interval, repeat=False)
        self.fig.tight_layout()
        self.canvas.draw()

    def start_analysis(self):
        self.show_loading_gif()  # Показываем анимацию загрузки
        func_str = self.task_field.toPlainText()
        self.analysis_thread = AnalysisThread(func_str)
        self.analysis_thread.analysis_finished.connect(self.display_analysis_results)  # Подключаем сигнал завершения анализа
        self.analysis_thread.analysis_failed.connect(self.display_analysis_error)  # Подключаем сигнал ошибки анализа
        self.analysis_thread.start()  # Запускаем поток анализа

    def show_loading_gif(self):
        self.loading_gif.setMovie(QMovie('loading.gif'))
        self.loading_gif.movie().start()  # Запускаем анимацию
        self.loading_gif.show()

    def hide_loading_gif(self):
        self.loading_gif.hide()

    def display_analysis_results(self, result):
        self.Analiz_table.setText(result)  # Отображаем результат анализа в таблице
        self.hide_loading_gif()

    def display_analysis_error(self, error_message):
        self.Analiz_table.setText(f'Ошибка анализа: {error_message}')
        self.hide_loading_gif()

    def clear_history(self):
        delete_history()  # Очищаем историю
        self.open_history_window()  # Открываем окно истории

    def open_history_window(self):
        self.history_window = HistoryWindow()  # Открываем окно истории
        self.history_window.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = X0yIllustrator()
    ex.show()  # Отображаем главное окно
    sys.exit(app.exec())  # Запуск приложения