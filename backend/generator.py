# библ для отправки запросов к LM St
import requests
#  для сбора ответов от модели
import json
import re  # добавлен для надёжного парсинга JSON

# Ад лок серв LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"


# Генерация опроса на основе клиент пути
# user_journey описание действий польз в приложении
# categories Список катег по которым нужно задать вопросы
def generate_survey(user_journey: str, categories: list) -> dict:
    # f-строка позволяет подст знач перем user_journey и categories
    prompt = f"""
Ты — генератор опросов удовлетворённости.
Клиентский путь пользователя:
{user_journey}
Категории для опроса: {', '.join(categories)}

ВАЖНО: Верни ТОЛЬКО JSON. Никакого текста до или после JSON. Никаких пояснений.

Сгенерируй опрос (3-5 вопросов). Формат — JSON строго как ниже:
{{
  "title": "Название опроса",
  "questions": [
    {{"text": "вопрос 1", "type": "rating", "category": "категория"}},
    {{"text": "вопрос 2", "type": "open", "category": "категория"}}
  ]
}}

Допустимые типы вопросов: rating, open.
Категория вопроса должна быть строго из списка: {', '.join(categories)}.
Только JSON, без пояснений.
"""

    # полезн нагруз для отправки к LM Studio
    load = {
        "model": "local-model",  # имя модели
        "messages": [  # Список сообщений для общ с моделью
            {
                "role": "system",  # Сист сообщ - задаёт роль модели
                "content": "Ты помощник для создания опросов. Ты возвращаешь только валидный JSON без пояснений."
            },
            {
                "role": "user",  # Сообщ от пользователя - сам запрос
                "content": prompt
            }
        ],
        "temperature": 0.7,  # Параметр креативност
        "max_tokens": 1200  
    }

    # json=load автоматически сериализует словарь в JSON и ставит header Content-Type
    response = requests.post(LM_STUDIO_URL, json=load)

    # Извлек текст ответа модели из JSON ответа сервера
    raw_text = response.json()["choices"][0]["message"]["content"]

    try:
        # Ищем позицию первого/посл символа '{'
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1

        # Если нашли  начало/конец/начало раньше конца
        if start != -1 and end > start:
            # Извлекподстроку с JSON и отпр её в словарь Python
            result = json.loads(raw_text[start:end])

            # === ДОБАВЛЕНА ВАЛИДАЦИЯ (исправление BUG-02 и BUG-03) ===
            # Проверяем структуру опроса
            if "title" not in result:
                result["title"] = "Опрос удовлетворённости"
            if "questions" not in result or not isinstance(result["questions"], list):
                result["questions"] = []

            # Валидируем каждый вопрос
            validated_questions = []
            for i, q in enumerate(result["questions"]):
                # Проверяем наличие category
                if "category" not in q or q["category"] not in categories:
                    # Если категория не указана или не из списка - исправляем
                    if categories:
                        q["category"] = categories[0]  # ставим первую категорию
                    else:
                        q["category"] = "общее"

                # Проверяем тип вопроса (исправление BUG-03)
                if "type" not in q or q["type"] not in ["rating", "open"]:
                    q["type"] = "open"  # ставим open как базовый тип

                # Проверяем наличие текста вопроса
                if "text" not in q or not q["text"]:
                    q["text"] = f"Оцените качество по категории '{q['category']}'"

                validated_questions.append(q)

            result["questions"] = validated_questions
            return result

        else:
            # Если не найден возвр ошибку и сырой ответ модели
            return {"error": "No JSON found", "raw": raw_text}
    except Exception as e:
        # любая ошибка - возвращаем её
        return {"error": str(e), "raw": raw_text}