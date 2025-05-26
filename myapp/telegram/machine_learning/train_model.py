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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# путь до файла: myapp\telegram\machine_learning\categorized_2024.json
CATEGORIZED_DATA_PATH = os.path.join(BASE_DIR, 'telegram', 'machine_learning', 'categorized_2024.json')
MODEL_PATH = os.path.join(BASE_DIR, 'telegram', 'machine_learning', 'telegram_category_model.joblib')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'telegram', 'machine_learning', 'telegram_category_vectorizer.joblib')

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

# Сохранение обновлённой базы данных
def save_categorized_data(data):
    os.makedirs(os.path.dirname(CATEGORIZED_DATA_PATH), exist_ok=True)
    with open(CATEGORIZED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Categorized data saved to {CATEGORIZED_DATA_PATH}")

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
def update_model(new_data, temp_data_path=None):
    categorized_data = load_categorized_data()
    existing_urls = {item['Post Url'] for item in categorized_data if 'Post Url' in item}

    # Если передан путь к temp_data, добавляем данные в categorized_2024.json
    if temp_data_path:
        try:
            with open(temp_data_path, 'r', encoding='utf-8') as f:
                temp_data = json.load(f)
            for item in temp_data:
                post_url = item['link']
                if post_url in existing_urls:
                    continue  # Пропускаем дубликат
                new_entry = {
                    "Social": "TG",
                    "Page url": f"https://t.me/{item['title']}",
                    "Post Url": post_url,
                    "Likes": item['reactions'],
                    "Reposts": item['forwards'],
                    "Comments": item['comments_count'],
                    "Views": item['views'],
                    "ER Post": 0.0,
                    "ER View": 0.0,
                    "VR": 0.0,
                    "Category ": item['category'],
                    "Text": item['message'],
                    "Date": item['date'],
                    "Type": "text"
                }
                categorized_data.append(new_entry)
                existing_urls.add(post_url)
            save_categorized_data(categorized_data)
        except FileNotFoundError:
            logging.error(f"Temp data file not found at {temp_data_path}")

    # Добавляем новые данные (из update_post_category)
    all_data = categorized_data + new_data
    texts = []
    categories = []
    for item in all_data:
        if not (item.get('Text') and item.get('Category ') is not None):
            continue

        text = item['Text']
        category = item['Category ']

        if not isinstance(category, str):
            category = str(category)
        category = category.strip().lower()

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

# Экспорт модели для использования в других проектах
def export_model(export_path):
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        export_model_path = os.path.join(export_path, 'telegram_category_model.joblib')
        export_vectorizer_path = os.path.join(export_path, 'telegram_category_vectorizer.joblib')
        os.makedirs(export_path, exist_ok=True)
        joblib.dump(model, export_model_path)
        joblib.dump(vectorizer, export_vectorizer_path)
        logging.info(f"Model and vectorizer exported to {export_model_path} and {export_vectorizer_path}")
        return True
    except FileNotFoundError:
        logging.error("Model or vectorizer not found for export.")
        return False