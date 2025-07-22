from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.category import Category

categories_bp = Blueprint('categories', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    categories = Category.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    })

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
    
    if data.get('type') not in ['income', 'expense']:
        return jsonify({'error': 'Tipo deve ser "income" ou "expense"'}), 400
    
    # Verificar se já existe uma categoria com o mesmo nome e tipo
    existing = Category.query.filter_by(
        user_id=user_id,
        name=data['name'],
        type=data['type']
    ).first()
    
    if existing:
        return jsonify({'error': 'Já existe uma categoria com este nome'}), 400
    
    category = Category(
        user_id=user_id,
        name=data['name'],
        type=data['type'],
        is_default=False
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify({
            'success': True,
            'category': category.to_dict(),
            'message': 'Categoria criada com sucesso'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar categoria'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404
    
    if category.is_default:
        return jsonify({'error': 'Não é possível editar categorias padrão'}), 400
    
    data = request.json
    
    if 'name' in data:
        # Verificar se já existe outra categoria com o mesmo nome e tipo
        existing = Category.query.filter_by(
            user_id=user_id,
            name=data['name'],
            type=category.type
        ).filter(Category.id != category_id).first()
        
        if existing:
            return jsonify({'error': 'Já existe uma categoria com este nome'}), 400
        
        category.name = data['name']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'category': category.to_dict(),
            'message': 'Categoria atualizada com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar categoria'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404
    
    if category.is_default:
        return jsonify({'error': 'Não é possível excluir categorias padrão'}), 400
    
    # Verificar se há transações associadas
    if category.transactions:
        return jsonify({'error': 'Não é possível excluir categoria com transações associadas'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Categoria excluída com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir categoria'}), 500

