from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import os

TABLE_NAME = "pois"

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# GET all POIs
# -----------------------------
@app.route('/api/pois', methods=['GET'])
def get_pois():
    conn = get_db_connection()
    pois = conn.execute(f'SELECT * FROM {TABLE_NAME}').fetchall()
    conn.close()
    return jsonify([dict(row) for row in pois])

# -----------------------------
# POST a new POI
# -----------------------------
@app.route('/api/pois', methods=['POST'])
def add_poi():
    data = request.get_json()

    # Extract fields (with simple validation)
    name = data.get('name')
    city = data.get('city')
    visits = data.get('visits')

    if not name or not city or visits is None:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            f'INSERT INTO {TABLE_NAME} (name, city, visits) VALUES (?, ?, ?)',
            (name, city, visits)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'POI added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# DELETE a POI by ID
# -----------------------------
@app.route('/api/pois/<int:poi_id>', methods=['DELETE'])
def delete_poi(poi_id):
    try:
        conn = get_db_connection()
        cur = conn.execute(f'DELETE FROM {TABLE_NAME} WHERE id = ?', (poi_id,))
        conn.commit()
        conn.close()

        if cur.rowcount == 0:
            return jsonify({'error': 'POI not found'}), 404

        return jsonify({'message': 'POI deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# UPDATE an existing POI by ID
# -----------------------------
@app.route('/api/pois/<int:poi_id>', methods=['PUT'])
def update_poi(poi_id):
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    visits = data.get('visits')

    if not name or not city or visits is None:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cur = conn.execute(
            f'UPDATE {TABLE_NAME} SET name = ?, city = ?, visits = ? WHERE id = ?',
            (name, city, visits, poi_id)
        )
        conn.commit()
        conn.close()

        if cur.rowcount == 0:
            return jsonify({'error': 'POI not found'}), 404

        return jsonify({'message': 'POI updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# Computes KPIs (total, average, top city)
# -----------------------------
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM pois', conn)
        conn.close()

        if df.empty:
            return jsonify({
                'total_visits': 0,
                'avg_visits': 0,
                'top_city': None
            })

        total_visits = int(df['visits'].sum())
        avg_visits = round(df['visits'].mean(), 2)

        # Group by city to find which city has the highest total visits
        top_city_row = df.groupby('city')['visits'].sum().sort_values(ascending=False).head(1)
        top_city = top_city_row.index[0]
        top_city_visits = int(top_city_row.iloc[0])

        return jsonify({
            'total_visits': total_visits,
            'avg_visits': avg_visits,
            'top_city': top_city,
            'top_city_visits': top_city_visits
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# Load CSV into database
# -----------------------------
@app.route('/api/load_csv', methods=['POST'])
def load_csv():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'file_path is required'}), 400
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {file_path}'}), 404

    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        # Ensure correct column names
        expected_cols = {'name', 'city', 'visits'}
        if not expected_cols.issubset(df.columns):
            return jsonify({'error': f'CSV must include columns: {expected_cols}'}), 400

        # Connect to DB and overwrite data
        conn = get_db_connection()
        df.to_sql('pois', conn, if_exists='replace', index=False)
        conn.close()

        return jsonify({
            'message': 'CSV loaded successfully',
            'rows': len(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# -----------------------------
# Upload CSV file from frontend
# -----------------------------
@app.route('/api/load_csv_upload', methods=['POST'])
def load_csv_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)

        # Ensure expected columns
        expected_cols = {'name', 'city', 'visits'}
        if not expected_cols.issubset(df.columns):
            return jsonify({'error': f'CSV must include columns: {expected_cols}'}), 400

        conn = get_db_connection()

        # Check if table exists
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                city TEXT,
                visits INTEGER
            )
        ''')

        # Insert rows (append, don’t replace)
        for _, row in df.iterrows():
            conn.execute(
                f'INSERT INTO {TABLE_NAME} (name, city, visits) VALUES (?, ?, ?)',
                (row['name'], row['city'], int(row['visits']))
            )
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'CSV uploaded successfully and data added to existing table',
            'rows': len(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
