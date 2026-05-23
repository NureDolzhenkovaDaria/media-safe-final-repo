import os
from flask import Flask, render_template, request, redirect
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

def get_db_connection():
    return pyodbc.connect(AZURE_CONN_STRING)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ItemID, Title, Author, MediaType, Status, UserRating, Notes FROM MediaItems ORDER BY ItemID DESC")
        items = cursor.fetchall()
        conn.close()
     
        return render_template('index.html', items=items)
    except Exception as e:
        return f"Помилка підключення до БД: {str(e)}", 500

@app.route('/add', methods=['POST'])
def add_item():
    title = request.form.get('title')
    media_type = request.form.get('media_type')
    rating = request.form.get('rating')

    if not title or not rating or not (1 <= int(rating) <= 10):
        return "Помилка валідації даних!", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MediaItems (UserID, Title, MediaType, Status, UserRating) VALUES (1, ?, ?, 'In Plans', ?)",
            (title, media_type, int(rating))
        )
        conn.commit()
        conn.close()
        return redirect('/')
    except Exception as e:
        return f"Помилка запису в БД: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
