from deep_translator import GoogleTranslator  # Альтернатива для перевода
import re
import wolframalpha


def translate_to_russian(text):
    try:
        translated_text = GoogleTranslator(source='auto', target='ru').translate(text)
        return format_translation(translated_text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


def format_translation(text):
    replacements = {
        r'\bR\b': 'R (все действительные числа)',
        r'элемент R': '∈ R',
        r'элемент Z': '∈ Z',
        r'2 π': '2π',
        r' \| ': ' на промежутке ',
        r'x\+': 'x',
        r'\(max{.*}\)': '',
        r'кратность \d+': '',
        r'abs\((.*?)\)': r'|\1|'
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r'\(все действительные числа\) \(все действительные числа\)', '(все действительные числа)', text)
    text = re.sub(r'\(предполагая функцию от реалов к реалам\)', '', text)
    text = re.sub(r'\((все неотрицательные действительные числа)\)', '', text)
    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'четная функция', 'чётная функция', text)
    return text.strip()


def get_function_characteristics(func_str):
    client = wolframalpha.Client("KJ3Q47-264X68Q8TK")

    queries = {
        "Область определения": f"domain of {func_str}",
        "Область значений": f"range of {func_str}",
        "Вершина": f"vertex of {func_str}",
        "Нули функции": f"zeros of {func_str}",
        "Чётность": f"is {func_str} even or odd"
    }

    results = {}
    for key, query in queries.items():
        res = client.query(query)
        if res['@success'] == 'false':
            results[key] = "Ошибка: нет данных"
        else:
            try:
                answer = next(res.results).text
                translated_answer = translate_to_russian(answer)
                results[key] = translated_answer
            except StopIteration:
                results[key] = "Ошибка: нет ответа"

    return results
