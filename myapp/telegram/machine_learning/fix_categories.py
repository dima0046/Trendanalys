import json
import os

# Путь к файлу
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIZED_DATA_PATH = os.path.join(BASE_DIR, 'machine_learning', 'categorized_2024.json')

# Загрузка данных
with open(CATEGORIZED_DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Исправление категорий
corrected_data = []
for item in data:
    category = item.get('Category ')
    if category is not None:
        # Приводим к строке, если не строка
        if not isinstance(category, str):
            category = str(category)
        # Убираем лишние пробелы и приводим к нижнему регистру
        category = category.strip().lower()
        item['Category '] = category
    corrected_data.append(item)

# Сохранение исправленных данных
with open(CATEGORIZED_DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(corrected_data, f, ensure_ascii=False, indent=4)

print("Categories in categorized_2024.json have been unified to lowercase with no extra spaces.")