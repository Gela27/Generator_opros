import re
from collections import Counter
from typing import List, Dict, Any


def extract_contacts(text: str) -> Dict[str, List[str]]:
    """Извлечение контактов из текстов"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\+?[\d\s\-\(\)]{10,20}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {
        "emails": list(set(emails))[:3],
        "phones": list(set(phones))[:3],
        "socials": []
    }


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    """Извлечение ключевых слов из текстов"""
    stop_words = {'и', 'в', 'на', 'с', 'по', 'за', 'из', 'у', 'о', 'при', 'к',
                  'это', 'что', 'как', 'так', 'все', 'уже', 'был', 'еще',
                  'пользователь', 'клиент', 'сайт', 'приложение', 'свой'}

    words = re.findall(r'[а-яА-ЯёЁ]{4,}', text.lower())
    words_filtered = [w for w in words if w not in stop_words]

    return [word for word, _ in Counter(words_filtered).most_common(top_n)]


def parsing_unstructured_data(text: str) -> Dict[str, Any]:
    """Парсинг неструктурированных данных: создание таблиц на основе длинных текстов"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    key_events = []
    problems = []
    successes = []

    problem_words = ['завис', 'тормоз', 'ошибк', 'не работает', 'проблем', 'медленн', 'сломал']
    success_words = ['быстро', 'удобно', 'отлично', 'хорошо', 'понравил', 'мгновенно']

    for sent in sentences:
        for word in problem_words:
            if word in sent.lower():
                problems.append(sent)
                break
        for word in success_words:
            if word in sent.lower():
                successes.append(sent)
                break

    return {
        "key_events": sentences[:3],
        "problems": problems[:3],
        "successes": successes[:2]
    }


def create_tables_from_data(text: str) -> List[Dict]:
    """Создание таблиц из разных типов данных"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    table = []
    for i, sent in enumerate(sentences[:5], 1):
        sentiment = "positive"
        if any(w in sent.lower() for w in ['проблем', 'завис', 'ошибк', 'медленн']):
            sentiment = "negative"
        elif any(w in sent.lower() for w in ['быстро', 'хорошо', 'удобно', 'отлично']):
            sentiment = "positive"
        else:
            sentiment = "neutral"

        table.append({
            "step": i,
            "description": sent[:50],
            "sentiment": sentiment
        })

    return table


def classify_by_categories(text: str, categories: List[str]) -> Dict[str, float]:
    """Классификация данных по категориям по заданному примеру"""
    result = {}
    text_lower = text.lower()

    category_keywords = {
        "скорость": ['быстро', 'медленн', 'скорость', 'загрузк', 'долго', 'мгновенно', 'быстрый'],
        "стабильность": ['завис', 'ошибк', 'падение', 'вылет', 'стабильн', 'сбой', 'краш'],
        "поддержка": ['помощ', 'поддержк', 'чат', 'оператор', 'ответили', 'бот', 'письмо'],
        "удобство": ['удобн', 'понятн', 'сложн', 'интуитивн', 'интерфейс', 'дизайн']
    }

    for category in categories:
        score = 0
        cat_keywords = category_keywords.get(category, [category.lower()])
        for keyword in cat_keywords:
            if keyword in text_lower:
                score += 1
        result[category] = min(score / 2, 1.0)

    return result


def sentiment_analysis_basic(text: str) -> Dict[str, Any]:
    """Базовый сентиментальный анализ текстов"""
    positive_words = ['хорошо', 'отлично', 'быстро', 'удобно', 'понравился', 'мгновенно', 'легко', 'прекрасно']
    negative_words = ['плохо', 'ужасно', 'завис', 'ошибка', 'медленно', 'сломалось', 'не работает', 'проблема']

    text_lower = text.lower()
    positive_count = sum(1 for w in positive_words if w in text_lower)
    negative_count = sum(1 for w in negative_words if w in text_lower)

    total = positive_count + negative_count
    if total == 0:
        score = 0
    else:
        score = (positive_count - negative_count) / total

    if score > 0.2:
        sentiment = "positive"
    elif score < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "score": round(score, 2),
        "sentiment": sentiment,
        "positive_matches": positive_count,
        "negative_matches": negative_count,
        "type": "basic"
    }


def sentiment_analysis_advanced(text: str) -> Dict[str, Any]:
    """Продвинутый сентиментальный анализ текстов"""
    sentiment_scores = {
        'отлично': 1.0, 'прекрасно': 0.9, 'хорошо': 0.7, 'нормально': 0.3,
        'удобно': 0.6, 'быстро': 0.7, 'мгновенно': 0.9, 'понравился': 0.8,
        'ужасно': -0.9, 'плохо': -0.7, 'завис': -0.6, 'ошибка': -0.5,
        'медленно': -0.5, 'сломалось': -0.8, 'не работает': -0.6, 'проблема': -0.4
    }

    text_lower = text.lower()
    scores = []

    sentences = re.split(r'[.!?]+', text_lower)
    by_stages = {}

    for i, sentence in enumerate(sentences[:5]):
        if len(sentence) > 10:
            sentence_score = 0
            for word, score in sentiment_scores.items():
                if word in sentence:
                    sentence_score += score
            if sentence_score != 0:
                by_stages[f"stage_{i + 1}"] = round(max(-1, min(1, sentence_score)), 2)
                scores.append(sentence_score)

    if not scores:
        overall = 0
    else:
        overall = sum(scores) / len(scores)

    overall = round(max(-1, min(1, overall)), 2)

    if overall > 0.3:
        sentiment = "positive"
    elif overall < -0.3:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "overall_score": overall,
        "sentiment": sentiment,
        "by_stages": by_stages,
        "confidence": min(0.9, len(scores) * 0.2),
        "type": "advanced"
    }


def write_interview_questions(topic: str, count: int = 5) -> List[str]:
    """Написание вопросов для интервью"""
    questions = [
        f"Как бы вы описали свой опыт использования {topic}?",
        f"С какими трудностями вы столкнулись при работе с {topic}?",
        f"Что вам больше всего понравилось в {topic}?",
        f"Что можно улучшить в {topic}?",
        f"Как часто вы пользуетесь {topic}?"
    ]
    return questions[:count]