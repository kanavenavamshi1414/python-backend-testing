from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# =========================
# CORS (frontend access)
# =========================
CORS(app, origins=["https://kanavena.shop"])

# =========================
# DATABASE CONFIG
# =========================

# ✍️ MASTER (WRITE DB)
db_write_config = {
    'host': 'private-database.c7uu8saq0zah.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Vamshi#147',
    'database': 'private-database'
}

# 👀 REPLICA (READ DB)
db_read_config = {
    'host': 'private-reader.c7uu8saq0zah.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Vamshi#147',
    'database': 'private-reader'
}

# =========================
# CONNECTION HELPERS
# =========================

def get_write_connection():
    return mysql.connector.connect(**db_write_config)

def get_read_connection():
    return mysql.connector.connect(**db_read_config)

def get_db_info(cursor):
    cursor.execute("SELECT @@hostname AS host, @@read_only AS read_only")
    return cursor.fetchone()

# =========================
# HEALTH CHECK (ALB)
# =========================
@app.route('/health')
def health():
    return "OK", 200

# =========================
# ROOT
# =========================
@app.route('/')
def index():
    return "Backend API Running", 200

# =========================
# READ APIs (REPLICA)
# =========================

@app.route('/users', methods=['GET'])
def get_users():
    conn = None
    cursor = None

    try:
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        db_info = get_db_info(cursor)

        return jsonify({
            "data": users,
            "served_by": db_info["host"],
            "read_only": db_info["read_only"],
            "db_role": "READER"
        })

    except Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =========================
# SINGLE USER (REPLICA)
# =========================

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = None
    cursor = None

    try:
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        db_info = get_db_info(cursor)

        return jsonify({
            "data": user,
            "served_by": db_info["host"],
            "db_role": "READER"
        })

    except Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =========================
# WRITE API (MASTER DB)
# =========================

@app.route('/users/add', methods=['POST'])
def add_user():
    conn = None
    cursor = None

    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and Email required'}), 400

    try:
        conn = get_write_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )

        conn.commit()

        return jsonify({'message': 'User added successfully'}), 201

    except Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =========================
# UPDATE USER (MASTER)
# =========================

@app.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    conn = None
    cursor = None

    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and Email required'}), 400

    try:
        conn = get_write_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404

        cursor.execute(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (name, email, user_id)
        )

        conn.commit()

        return jsonify({'message': 'User updated successfully'})

    except Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =========================
# DELETE USER (MASTER)
# =========================

@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = None
    cursor = None

    try:
        conn = get_write_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({'message': 'User deleted successfully'})

    except Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# =========================
# ENTRY POINT
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
