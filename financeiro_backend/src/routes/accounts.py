from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.account import Account
from datetime import datetime
from decimal import Decimal, InvalidOperation

accounts_bp = Blueprint('accounts', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@accounts_bp.route('/accounts', methods=['GET'])
def get_accounts():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    accounts = Account.query.filter_by(user_id=user_id).all()
    return jsonify({'accounts': [account.to_dict() for account in accounts]})

@accounts_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Conta não encontrada'}), 404
    
    return jsonify({'account': account.to_dict()})

@accounts_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Conta não encontrada'}), 404
    
    data = request.json
    
    try:
        if 'name' in data:
            account.name = data['name']
        
        if 'balance' in data:
            account.balance = Decimal(str(data['balance']))
        
        account.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'account': account.to_dict(),
            'message': 'Conta atualizada com sucesso'
        })
    except (InvalidOperation, ValueError):
        return jsonify({'error': 'Saldo inválido'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar conta: {str(e)}'}), 500

@accounts_bp.route('/accounts', methods=['POST'])
def create_account():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Nome da conta é obrigatório'}), 400
    
    account = Account(
        user_id=user_id,
        name=data['name'],
        balance=data.get('balance', 0.00)
    )
    
    try:
        db.session.add(account)
        db.session.commit()
        return jsonify({
            'success': True,
            'account': account.to_dict(),
            'message': 'Conta criada com sucesso'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar conta'}), 500

