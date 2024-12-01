import sqlite3  # Импортируем модуль для работы с базой данных SQLite
from PyQt6.QtCore import QDateTime  # Импортируем QDateTime для работы с текущей датой и временем


# Функция для сохранения функции в историю запросов
def save_function_to_history(func_str):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect("History_of_req.sqlite")
    cursor = connection.cursor()

    # Получаем текущую дату и время в формате "год-месяц-день часы:минуты:секунды"
    created_at = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

    # SQL-запрос для вставки функции и времени создания в таблицу 'functions'
    cursor.execute("INSERT INTO functions (function, created_at) VALUES (?, ?)", (func_str, created_at))

    connection.commit()  # Сохраняем изменения в базе данных
    connection.close()  # Закрываем соединение с базой данных


# Функция для загрузки истории запросов из базы данных
def load_history():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect("History_of_req.sqlite")
    cursor = connection.cursor()

    # SQL-запрос для получения всех записей из таблицы 'functions', упорядоченных по дате создания (в порядке убывания)
    cursor.execute("SELECT function, created_at FROM functions ORDER BY created_at DESC")

    data = cursor.fetchall()  # Извлекаем все строки результата запроса
    connection.close()  # Закрываем соединение с базой данных
    return data  # Возвращаем список с историей запросов


# Функция для удаления всех записей из истории
def delete_history():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect("History_of_req.sqlite")
    cursor = connection.cursor()

    # SQL-запрос для удаления всех записей из таблицы 'functions'
    cursor.execute("DELETE FROM functions")  # Удаление всех строк из таблицы

    connection.commit()  # Сохраняем изменения в базе данных
    connection.close()  # Закрываем соединение с базой данных