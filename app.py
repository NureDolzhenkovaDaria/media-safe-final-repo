import os
from flask import Flask, render_template_string, request, redirect
import pyodbc

app = Flask(__name__)

AZURE_CONN_STRING = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:media-safe-sqlserver-del.database.windows.net,1433;"
    "Database=media-safe-db;"
    "Uid=azureuser;"
    "Pwd=~XEa>!4Fk~9&>J+;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Хмарний медіа-сейф</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .media-card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
<div class="container py-4" style="max-width: 500px;">
    <header class="text-center mb-4">
        <h1 class="h3 fw-bold text-primary">📱 Хмарний медіа-сейф</h1>
        <p class="text-muted">Персональний трекер медіа-контенту</p>
    </header>

    <div class="card p-3 mb-4 shadow-sm">
        <h5 class="fw-bold mb-3">➕ Додати до медіатеки</h5>
        <form action="/add" method="POST">
            <div class="mb-2">
                <input type="text" name="title" class="form-control" placeholder="Назва (напр. Грокнемо алгоритми)" required>
            </div>
            <div class="mb-2">
                <select name="media_type" class="form-select">
                    <option value="Book">Книга</option>
                    <option value="Anime">Аніме</option>
                    <option value="Music">Музика</option>
                </select>
            </div>
            <div class="mb-2">
                <input type="number" name="rating" class="form-control" placeholder="Оцінка (1-10)" min="1" max="10" required>
            </div>
            <button type="submit" class="btn btn-primary w-100 fw-bold">Зберегти в Azure SQL</button>
        </form>
    </div>

    <h5 class="fw-bold mb-3">📋 Моя медіатека:</h5>
    {% if items %}
        {% for item in items %}
        <div class="card media-card p-3 mb-2 bg-white">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="fw-bold m-0">{{ item[1] }}</h6>
                    <small class="text-muted">Тип: {{ item[3] }}</small>
                </div>
                <span class="badge bg-warning text-dark">⭐ {{ item[5] }}/10</span>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p class="text-center text-muted">Медіатека порожня. Додайте перший елемент!</p>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        conn = pyodbc.connect(AZURE_CONN_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT ItemID, Title, Author, MediaType, Status, UserRating, Notes FROM MediaItems ORDER BY ItemID DESC")
        items = cursor.fetchall()
        conn.close()
        return render_template_string(HTML_TEMPLATE, items=items)
    except Exception as e:
        return f"Помилка підключення до БД: {str(e)}"

@app.route('/add', methods=['POST'])
def add_item():
    title = request.form.get('title')
    media_type = request.form.get('media_type')
    rating = request.form.get('rating')

    if not title or not rating or not (1 <= int(rating) <= 10):
        return "Помилка валідації даних!", 400

    try:
        conn = pyodbc.connect(AZURE_CONN_STRING)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MediaItems (UserID, Title, MediaType, Status, UserRating) VALUES (1, ?, ?, 'In Plans', ?)",
            (title, media_type, int(rating))
        )
        conn.commit()
        conn.close()
        return redirect('/')
    except Exception as e:
        return f"Помилка запису в БД: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
