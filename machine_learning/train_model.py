# machine_learning/train_model.py
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import logging
import nltk
from nltk.corpus import stopwords

# Загрузка стоп-слов для русского языка
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
russian_stop_words = stopwords.words('russian')

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIZED_DATA_PATH = os.path.join(BASE_DIR, 'machine_learning', 'categorized_2024.json')
MODEL_PATH = os.path.join(BASE_DIR, 'machine_learning', 'telegram_category_model.joblib')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'machine_learning', 'telegram_category_vectorizer.joblib')

# Загрузка прокатегоризированной базы
def load_categorized_data():
    try:
        with open(CATEGORIZED_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Унификация категорий при загрузке
        for item in data:
            category = item.get('Category ')
            if category is not None:
                if not isinstance(category, str):
                    category = str(category)
                item['Category '] = category.strip().lower()
        return data
    except FileNotFoundError:
        logging.error(f"Categorized data file not found at {CATEGORIZED_DATA_PATH}")
        return []

# Инициализация и обучение модели
def train_model():
    categorized_data = load_categorized_data()
    if not categorized_data:
        logging.warning("No categorized data available for training.")
        return None, None

    texts = []
    categories = []
    for item in categorized_data:
        # Проверяем наличие полей 'Text' и 'Category '
        if not (item.get('Text') and item.get('Category ') is not None):
            continue

        text = item['Text']
        category = item['Category ']

        # Пропускаем записи, где категория пустая
        if not category:
            continue

        texts.append(text)
        categories.append(category)

    if not texts or not categories:
        logging.warning("No valid text or categories found for training.")
        return None, None

    vectorizer = TfidfVectorizer(max_features=5000, stop_words=russian_stop_words)
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, categories)

    # Создание папки, если её нет
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logging.info(f"Model and vectorizer saved to {MODEL_PATH} and {VECTORIZER_PATH}")
    return model, vectorizer

# Загрузка сохранённой модели
def load_model():
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        logging.info("Loaded existing model and vectorizer.")
        return model, vectorizer
    except FileNotFoundError:
        logging.warning("No trained model found, training a new one...")
        return train_model()

# Категоризация нового поста
def predict_category(text, model, vectorizer):
    if not model or not vectorizer:
        return "не определено"
    if not text:
        return "не определено"
    X_new = vectorizer.transform([text])
    return model.predict(X_new)[0]

# Обновление модели с новыми данными
def update_model(new_data):
    categorized_data = load_categorized_data()
    all_data = categorized_data + new_data
    texts = []
    categories = []
    for item in all_data:
        if not (item.get('Text') and item.get('Category ') is not None):
            continue

        text = item['Text']
        category = item['Category ']

        # Унифицируем категорию
        if not isinstance(category, str):
            category = str(category)
        category = category.strip().lower()

        # Пропускаем записи, где категория пустая
        if not category:
            continue

        texts.append(text)
        categories.append(category)

    if not texts or not categories:
        logging.warning("No valid data for model update.")
        return

    vectorizer = TfidfVectorizer(max_features=5000, stop_words=russian_stop_words)
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, categories)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logging.info(f"Model and vectorizer updated and saved to {MODEL_PATH} and {VECTORIZER_PATH}")

# Получение уникальных категорий
def get_unique_categories():
    categorized_data = load_categorized_data()
    categories = set()
    for item in categorized_data:
        category = item.get('Category ')
        if category is not None and category:
            categories.add(category)
    return sorted(categories)