from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

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
if __name__ == '__main__':
    app.run(debug=True)
