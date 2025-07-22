from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.credit_card import CreditCard
from datetime import datetime

credit_cards_bp = Blueprint('credit_cards', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@credit_cards_bp.route('/credit-cards', methods=['GET'])
def get_credit_cards():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    credit_cards = CreditCard.query.filter_by(user_id=user_id).all()
    return jsonify({'credit_cards': [card.to_dict() for card in credit_cards]})

@credit_cards_bp.route('/credit-cards/<int:card_id>', methods=['GET'])
def get_credit_card(card_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
    
    if not card:
        return jsonify({'error': 'Cartão não encontrado'}), 404
    
    return jsonify({'credit_card': card.to_dict()})

@credit_cards_bp.route('/credit-cards', methods=['POST'])
def create_credit_card():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Nome do cartão é obrigatório'}), 400
    
    if not data.get('closing_day') or not (1 <= data.get('closing_day') <= 31):
        return jsonify({'error': 'Dia de fechamento deve estar entre 1 e 31'}), 400
    
    card = CreditCard(
        user_id=user_id,
        name=data['name'],
        closing_day=data['closing_day'],
        current_balance=data.get('current_balance', 0.00)
    )
    
    try:
        db.session.add(card)
        db.session.commit()
        return jsonify({
            'success': True,
            'credit_card': card.to_dict(),
            'message': 'Cartão criado com sucesso'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar cartão'}), 500

@credit_cards_bp.route('/credit-cards/<int:card_id>', methods=['PUT'])
def update_credit_card(card_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
    
    if not card:
        return jsonify({'error': 'Cartão não encontrado'}), 404
    
    data = request.json
    
    if 'name' in data:
        card.name = data['name']
    
    if 'closing_day' in data:
        if not (1 <= data['closing_day'] <= 31):
            return jsonify({'error': 'Dia de fechamento deve estar entre 1 e 31'}), 400
        card.closing_day = data['closing_day']
    
    if 'current_balance' in data:
        card.current_balance = data['current_balance']
    
    card.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'credit_card': card.to_dict(),
            'message': 'Cartão atualizado com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar cartão'}), 500

@credit_cards_bp.route('/credit-cards/<int:card_id>', methods=['DELETE'])
def delete_credit_card(card_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
    
    if not card:
        return jsonify({'error': 'Cartão não encontrado'}), 404
    
    # Verificar se há transações associadas
    if card.transactions:
        return jsonify({'error': 'Não é possível excluir cartão com transações associadas'}), 400
    
    try:
        db.session.delete(card)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Cartão excluído com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir cartão'}), 500

