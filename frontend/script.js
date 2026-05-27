const API_URL = 'http://localhost:8000/generate';
let currentAbortController = null;

document.getElementById('selectAllBtn').addEventListener('click', () => {
    document.querySelectorAll('.feature-checkbox input').forEach(cb => {
        cb.checked = true;
    });
});

document.getElementById('clearAllBtn').addEventListener('click', () => {
    document.querySelectorAll('.feature-checkbox input').forEach(cb => {
        cb.checked = false;
    });
});

document.getElementById('generateBtn').addEventListener('click', async () => {
    const userJourney = document.getElementById('journey').value.trim();
    const categoriesInput = document.getElementById('categories').value.trim();

    const selectedFeatures = [];
    document.querySelectorAll('.feature-checkbox input:checked').forEach(cb => {
        selectedFeatures.push(cb.value);
    });

    const sentimentValue = document.querySelector('input[name="sentiment"]:checked').value;
    selectedFeatures.push(sentimentValue);

    if (!userJourney) {
        showError('Заполните клиентский путь');
        return;
    }

    if (!categoriesInput) {
        showError('Укажите категории');
        return;
    }

    let categories = categoriesInput.split(',').map(c => c.trim()).filter(c => c);

    if (categories.length === 0) {
        showError('Укажите хотя бы одну категорию');
        return;
    }

    if (selectedFeatures.length === 0) {
        showError('Выберите хотя бы одну функцию');
        return;
    }

    if (currentAbortController) {
        currentAbortController.abort();
    }

    showLoading();
    hideError();
    hideOutput();
    showCancelButton(true);

    currentAbortController = new AbortController();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_journey: userJourney,
                categories: categories,
                features: selectedFeatures
            }),
            signal: currentAbortController.signal
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        displaySurvey(data);

    } catch (error) {
        if (error.name === 'AbortError') {
            showError('Генерация отменена');
        } else {
            showError(error.message);
        }
    } finally {
        hideLoading();
        showCancelButton(false);
        currentAbortController = null;
    }
});

document.getElementById('cancelBtn').addEventListener('click', () => {
    if (currentAbortController) {
        currentAbortController.abort();
    }
});

document.getElementById('journey').addEventListener('input', function() {
    const charCount = this.value.length;
    document.getElementById('charCount').textContent = charCount;
    if (charCount > 2000) {
        this.value = this.value.slice(0, 2000);
        document.getElementById('charCount').textContent = 2000;
    }
});

function displaySurvey(survey) {
    document.getElementById('surveyTitle').textContent = survey.title || 'Опрос удовлетворённости';

    const questionsList = document.getElementById('questionsList');
    questionsList.innerHTML = '';

    if (survey.questions && survey.questions.length > 0) {
        survey.questions.forEach((q, index) => {
            const card = document.createElement('div');
            card.className = 'question-card';
            card.innerHTML = `
                <div class="question-text">${index + 1}. ${q.text}</div>
                <div class="question-meta">
                    <span class="question-type">${q.type === 'rating' ? 'Рейтинг (1-5)' : 'Открытый ответ'}</span>
                    <span class="question-category">${q.category}</span>
                </div>
            `;
            questionsList.appendChild(card);
        });
    } else {
        questionsList.innerHTML = '<p>Нет сгенерированных вопросов</p>';
    }

    const analysisDiv = document.getElementById('analysisResults');
    const analysisGrid = document.getElementById('analysisGrid');

    if (survey.analysis_results && Object.keys(survey.analysis_results).length > 0) {
        analysisGrid.innerHTML = '';

        for (const [key, value] of Object.entries(survey.analysis_results)) {
            const card = document.createElement('div');
            card.className = 'analysis-card';

            let title = '';
            let content = '';

            if (key === 'keywords') {
                title = 'Ключевые слова';
                content = value.join(', ');
            } else if (key === 'contacts') {
                title = 'Контакты';
                content = '';
                if (value.emails && value.emails.length) content += `Email: ${value.emails.join(', ')}<br>`;
                if (value.phones && value.phones.length) content += `Телефоны: ${value.phones.join(', ')}`;
                if (!content) content = 'Не найдено';
            } else if (key === 'parsed_data') {
                title = 'Парсинг данных';
                content = '';
                if (value.problems && value.problems.length) content += `Проблемы: ${value.problems[0].substring(0, 80)}...<br>`;
                if (value.successes && value.successes.length) content += `Успехи: ${value.successes[0].substring(0, 80)}...`;
                if (!content) content = 'Данные проанализированы';
            } else if (key === 'classification') {
                title = 'Классификация';
                content = Object.entries(value).map(([cat, score]) => `${cat}: ${Math.round(score * 100)}%`).join('<br>');
            } else if (key === 'sentiment_basic') {
                title = 'Сентимент анализ (Базовый)';
                let sentimentRu = '';
                if (value.sentiment === 'positive') sentimentRu = 'Положительный';
                else if (value.sentiment === 'negative') sentimentRu = 'Отрицательный';
                else sentimentRu = 'Нейтральный';
                content = `Тон: ${sentimentRu}<br>Оценка: ${value.score}<br>Позитивных слов: ${value.positive_matches}<br>Негативных слов: ${value.negative_matches}`;
            } else if (key === 'sentiment_advanced') {
                title = 'Сентимент анализ (Продвинутый)';
                let sentimentRu = '';
                if (value.sentiment === 'positive') sentimentRu = 'Положительный';
                else if (value.sentiment === 'negative') sentimentRu = 'Отрицательный';
                else sentimentRu = 'Нейтральный';
                content = `Общий тон: ${sentimentRu}<br>Оценка: ${value.overall_score}<br>Уверенность: ${Math.round(value.confidence * 100)}%`;
                if (value.by_stages && Object.keys(value.by_stages).length > 0) {
                    content += '<br>По этапам:<br>';
                    for (const [stage, score] of Object.entries(value.by_stages)) {
                        content += `${stage}: ${score}<br>`;
                    }
                }
            } else if (key === 'tables') {
                title = 'Создание таблиц';
                if (Array.isArray(value) && value.length) {
                    content = '<table style="width:100%; font-size:12px; border-collapse:collapse;">';
                    content += '<tr><th style="border:1px solid #ddd; padding:4px;">Шаг</th><th style="border:1px solid #ddd; padding:4px;">Описание</th><th style="border:1px solid #ddd; padding:4px;">Тон</th></tr>';
                    value.forEach(row => {
                        content += `<tr><td style="border:1px solid #ddd; padding:4px;">${row.step}</td><td style="border:1px solid #ddd; padding:4px;">${row.description}</td><td style="border:1px solid #ddd; padding:4px;">${row.sentiment}</td></tr>`;
                    });
                    content += '</table>';
                } else {
                    content = 'Таблица создана';
                }
            } else {
                title = key;
                content = JSON.stringify(value).substring(0, 150);
            }

            card.innerHTML = `<h4>${title}</h4><p>${content}</p>`;
            analysisGrid.appendChild(card);
        }

        analysisDiv.style.display = 'block';
    } else {
        analysisDiv.style.display = 'none';
    }

    document.getElementById('outputSection').style.display = 'block';
}

function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('generateBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
    document.getElementById('generateBtn').disabled = false;
}

function showCancelButton(show) {
    const cancelBtn = document.getElementById('cancelBtn');
    const generateBtn = document.getElementById('generateBtn');
    if (show) {
        cancelBtn.style.display = 'block';
        generateBtn.style.display = 'none';
    } else {
        cancelBtn.style.display = 'none';
        generateBtn.style.display = 'block';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function hideOutput() {
    document.getElementById('outputSection').style.display = 'none';
    document.getElementById('analysisResults').style.display = 'none';
}