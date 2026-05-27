from flask import Flask, request, jsonify #интерфейс, запросы, json для браузера
from flask_cors import CORS #для разрешения запросов с разных адресов
from generator import generate_survey_with_features

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/generate', methods=['POST'])
def generate_api():
    try:
        data = request.json
        user_journey = data.get('user_journey', '')
        categories = data.get('categories', [])
        selected_features = data.get('features', [])

        if not user_journey:
            return jsonify({"error": "Заполните клиентский путь"}), 400

        if not categories or len(categories) == 0:
            return jsonify({"error": "Укажите хотя бы одну категорию"}), 400

        if not selected_features:
            selected_features = ["write_questions", "parse_data", "extract_contacts",
                                 "create_tables", "extract_keywords", "classify",
                                 "sentiment_basic", "sentiment_advanced"]

        result = generate_survey_with_features(user_journey, categories, selected_features)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500

if __name__ == "__main__":
    print("Сервер запущен на http://localhost:8000")
    app.run(debug=True, port=8000)