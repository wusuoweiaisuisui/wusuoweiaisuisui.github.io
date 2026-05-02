from flask import Flask, request, jsonify
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os
import ssl

app = Flask(__name__)
DATABASE = 'users.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0,
            api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            provider TEXT,
            model TEXT,
            tokens INTEGER,
            cost REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key():
    """生成API密钥"""
    return 'sk-' + secrets.token_urlsafe(32)

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': '请填写完整信息'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            conn.close()
            return jsonify({'error': '用户名或邮箱已存在'}), 400

        password_hash = hash_password(password)
        api_key = generate_api_key()

        c.execute('''
            INSERT INTO users (username, email, password_hash, api_key, balance)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, api_key, 0))

        conn.commit()
        user_id = c.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'api_key': api_key,
                'balance': 0
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': '请填写完整信息'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if not user or user['password_hash'] != hash_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401

        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'balance': user['balance'],
                'api_key': user['api_key']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, email, balance, api_key, created_at, status FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'balance': user['balance'],
        'api_key': user['api_key'],
        'created_at': user['created_at'],
        'status': user['status']
    })

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, email, balance, api_key, created_at, status FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return jsonify({'users': [dict(user) for user in users], 'total': len(users)})

@app.route('/api/recharge', methods=['POST'])
def recharge():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    if not all([user_id, amount]):
        return jsonify({'error': '参数不完整'}), 400

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
        c.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, "recharge", ?, "账户充值")', (user_id, amount))
        conn.commit()
        c.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        new_balance = c.fetchone()['balance']
        conn.close()
        return jsonify({'success': True, 'message': '充值成功', 'new_balance': new_balance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '用户已删除'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total_users FROM users')
    total_users = c.fetchone()['total_users']
    c.execute('SELECT SUM(balance) as total_balance FROM users')
    total_balance = c.fetchone()['total_balance'] or 0
    c.execute('SELECT COUNT(*) as total_transactions FROM transactions')
    total_transactions = c.fetchone()['total_transactions']
    conn.close()
    return jsonify({'total_users': total_users, 'total_balance': total_balance, 'total_transactions': total_transactions})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'User Management System', 'timestamp': datetime.now().isoformat()})

@app.route('/')
def index():
    return jsonify({
        'name': '虾仔科技 - 用户管理系统',
        'version': '1.0.0',
        'endpoints': {
            'register': '/api/register',
            'login': '/api/login',
            'user_info': '/api/user/<id>',
            'admin_users': '/api/admin/users',
            'admin_stats': '/api/admin/stats',
            'recharge': '/api/recharge'
        }
    })

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("用户管理系统初始化完成！")
    print("数据库文件: users.db")
    print("服务端口: 443 (HTTPS)")
    print("=" * 50)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')

    app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False)
