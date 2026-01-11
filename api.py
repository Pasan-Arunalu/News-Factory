from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = sqlite3.connect('news_data.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch only rewritten articles, latest first
        cursor.execute("""
            SELECT id, title, body, status 
            FROM articles 
            WHERE status = 'rewritten' 
            ORDER BY id DESC 
            LIMIT 20
        """)

        rows = cursor.fetchall()
        conn.close()

        # Convert SQL rows into a list of dictionaries for JSON
        news_list = []
        for row in rows:
            news_list.append({
                "id": row['id'],
                "title": row['title'],
                "body": row['body']
            })

        return jsonify(news_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run on port 5000
    print("News API is running on http://127.0.0.1:5000/api/news")
    app.run(debug=True, port=5000)