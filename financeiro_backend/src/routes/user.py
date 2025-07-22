from flask import Blueprint, jsonify, request, session
from src.models.user import User, db

user_bp = Blueprint('auth', __name__)

@user_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Usuário e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == password:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Login realizado com sucesso'
        })
    else:
        return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

@user_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@user_bp.route('/auth/check', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
    
    return jsonify({'authenticated': False}), 401
