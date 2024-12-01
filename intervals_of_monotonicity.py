import wolframalpha  # Импорт библиотеки для работы с WolframAlpha API
import re


def analyze_and_translate_function(func_str):
    client = wolframalpha.Client("KJ3Q47-264X68Q8TK")

    # Словарь запросов, где ключ — описание результата на русском, а значение — текст запроса для WolframAlpha
    queries = {
        "Промежутки монотонности": f"intervals of monotonicity of {func_str}",
        # Запрос для поиска промежутков монотонности функции
    }

    # Словарь для хранения результатов ответа от WolframAlpha
    results = {}
    for key, query in queries.items():
        # Отправка запроса к WolframAlpha
        res = client.query(query)

        # Проверка успешности выполнения запроса
        if res['@success'] == 'false':
            results[key] = "Ошибка: нет данных"  # Если запрос не удался, записываем сообщение об ошибке
        else:
            try:
                # Извлекаем текст ответа из результатов запроса
                answer = next(res.results).text
                results[key] = answer  # Сохраняем полученный ответ в словарь
            except StopIteration:
                results[key] = "Ошибка: нет ответа"  # Если нет результатов, записываем сообщение об ошибке

    def translate_to_russian(text):
        # Словарь замен для перевода терминов и выражений с английского на русский
        replacements = {
            "increasing": "увеличивается",  # Перевод термина "increasing" (возрастание)
            "decreasing": "уменьшается",  # Перевод термина "decreasing" (убывание)
            "on": "на промежутке",  # Перевод термина "on"
            "is": ""  # Удаление слова "is" (ненужное в переводе)
        }

        # Замена английских терминов на их русские аналоги
        for english, russian in replacements.items():
            text = re.sub(english, russian, text)  # Применяем каждую замену в тексте

        return text  # Возвращаем переведённый текст

    # Создание нового словаря для переведённых результатов
    translated_results = {}
    for key, value in results.items():
        translated_value = translate_to_russian(value)  # Переводим текст результата
        translated_results[key] = translated_value  # Сохраняем переведённый результат

    return translated_results  # Возвращаем словарь с переведёнными результатами
