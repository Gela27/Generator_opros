import requests
import json
import re
from typing import List, Dict
from analysis import (
    extract_contacts, extract_keywords, parsing_unstructured_data,
    create_tables_from_data, classify_by_categories,
    sentiment_analysis_basic, sentiment_analysis_advanced
)

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"


def generate_personalized_survey(user_journey: str, categories: List[str], analysis_results: Dict) -> Dict:
    """Генератор персонализированных опросов на основе клиентского пути"""

    problems = analysis_results.get('parsed_data', {}).get('problems', [])
    successes = analysis_results.get('parsed_data', {}).get('successes', [])
    keywords = analysis_results.get('keywords', [])
    sentiment = analysis_results.get('sentiment_basic', {}).get('sentiment', 'neutral')

    prompt = f"""
Ты генератор персонализированных опросов. Проанализируй клиентский путь пользователя и создай вопросы.

КЛИЕНТСКИЙ ПУТЬ:
{user_journey}

КАТЕГОРИИ ДЛЯ ОПРОСА: {', '.join(categories)}

РЕЗУЛЬТАТЫ АНАЛИЗА:
- Проблемы: {problems}
- Успехи: {successes}
- Ключевые слова: {keywords[:5]}
- Тональность: {sentiment}

Твоя задача - создать 3-5 ПЕРСОНАЛИЗИРОВАННЫХ вопросов, которые:
1. Учитывают конкретные проблемы пользователя
2. Спрашивают про то, что понравилось
3. Предлагают улучшения на основе опыта

Типы вопросов:
- rating: оценка от 1 до 5
- open: открытый вопрос

Верни ТОЛЬКО JSON:
{{"title": "Персонализированный опрос", "questions": [{{"text": "вопрос", "type": "rating", "category": "категория"}}]}}

Вопросы должны быть КОНКРЕТНЫМИ под эту ситуацию!
"""

    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 800
    }

    try:
        resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        raw_text = resp.json()["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
            return result
        return {"title": "Опрос", "questions": []}
    except Exception as e:
        print(f"Ошибка генерации опроса: {e}")
        return {"title": "Опрос", "questions": []}


def generate_survey_with_features(user_journey: str, categories: List[str], selected_features: List[str]) -> Dict:
    results = {
        "title": "Опрос удовлетворенности",
        "questions": [],
        "selected_features": selected_features,
        "analysis_results": {}
    }
    # Анализ клиент. пути выполняем только те функции, которые выбрал пользователь через галочки
    # Каждая функция анализирует текст и сохраняет результат в словарь analysis_results
    if "extract_contacts" in selected_features:
        results["analysis_results"]["contacts"] = extract_contacts(user_journey)

    if "extract_keywords" in selected_features:
        results["analysis_results"]["keywords"] = extract_keywords(user_journey)

    if "parse_data" in selected_features:
        results["analysis_results"]["parsed_data"] = parsing_unstructured_data(user_journey)

    if "create_tables" in selected_features:
        results["analysis_results"]["tables"] = create_tables_from_data(user_journey)

    if "classify" in selected_features:
        results["analysis_results"]["classification"] = classify_by_categories(user_journey, categories)

    if "sentiment_basic" in selected_features:
        results["analysis_results"]["sentiment_basic"] = sentiment_analysis_basic(user_journey)

    if "sentiment_advanced" in selected_features:
        results["analysis_results"]["sentiment_advanced"] = sentiment_analysis_advanced(user_journey)

    # Генерация персонал. опроса на основе анализа
    survey = generate_personalized_survey(user_journey, categories, results["analysis_results"])
    results["title"] = survey.get("title", "Персонализированный опрос")
    results["questions"] = survey.get("questions", [])

    return results