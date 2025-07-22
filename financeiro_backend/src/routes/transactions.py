from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.transaction import Transaction
from src.models.account import Account
from src.models.credit_card import CreditCard
from src.models.category import Category
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from decimal import Decimal, InvalidOperation

transactions_bp = Blueprint('transactions', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@transactions_bp.route('/transactions', methods=['GET'])
def get_transactions():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    
    # Parâmetros de filtro
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')  # 'income' ou 'expense'
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    # Query base
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Filtros de data
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= start_date)
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para start_date'}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= end_date)
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para end_date'}), 400
    
    # Filtro por tipo (baseado na categoria)
    if transaction_type:
        query = query.join(Category).filter(Category.type == transaction_type)
    
    # Ordenação e paginação
    query = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    
    total = query.count()
    transactions = query.offset((page - 1) * limit).limit(limit).all()
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit
    })

@transactions_bp.route('/transactions', methods=['POST'])
def create_transaction():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    data = request.json
    
    # Validações básicas
    required_fields = ['description', 'amount', 'transaction_date', 'category_id', 'payment_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    # Validar categoria
    category = Category.query.filter_by(id=data['category_id'], user_id=user_id).first()
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404
    
    # Validar tipo de pagamento
    if data['payment_type'] not in ['debit', 'pix', 'credit_card']:
        return jsonify({'error': 'Tipo de pagamento inválido'}), 400
    
    # Validar data
    try:
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de data inválido'}), 400
    
    # Validações específicas por tipo de pagamento
    account_id = None
    credit_card_id = None
    
    if data['payment_type'] in ['debit', 'pix']:
        if not data.get('account_id'):
            return jsonify({'error': 'Conta é obrigatória para débito/PIX'}), 400
        
        account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first()
        if not account:
            return jsonify({'error': 'Conta não encontrada'}), 404
        account_id = account.id
        
    elif data['payment_type'] == 'credit_card':
        if not data.get('credit_card_id'):
            return jsonify({'error': 'Cartão é obrigatório para pagamento no cartão de crédito'}), 400
        
        credit_card = CreditCard.query.filter_by(id=data['credit_card_id'], user_id=user_id).first()
        if not credit_card:
            return jsonify({'error': 'Cartão não encontrado'}), 404
        credit_card_id = credit_card.id
    
    # Número de parcelas
    installments = int(data.get('installments', 1))
    if installments < 1:
        return jsonify({'error': 'Número de parcelas deve ser maior que 0'}), 400
    
    # Se for cartão de crédito e mais de 1 parcela, validar
    if data['payment_type'] == 'credit_card' and installments > 1:
        if installments > 24:
            return jsonify({'error': 'Máximo de 24 parcelas'}), 400
    elif data['payment_type'] in ['debit', 'pix'] and installments > 1:
        return jsonify({'error': 'Débito e PIX não podem ser parcelados'}), 400
    
    try:
        # Criar transação principal
        try:
            amount = Decimal(str(data['amount']))
        except (InvalidOperation, ValueError):
            return jsonify({'error': 'Valor inválido'}), 400
            
        installment_amount = amount / installments if installments > 1 else amount
        
        main_transaction = Transaction(
            user_id=user_id,
            category_id=category.id,
            account_id=account_id,
            credit_card_id=credit_card_id,
            description=data['description'],
            amount=installment_amount,
            transaction_date=transaction_date,
            payment_type=data['payment_type'],
            installments=installments,
            installment_number=1
        )
        
        db.session.add(main_transaction)
        db.session.flush()  # Para obter o ID
        
        created_transactions = [main_transaction]
        
        # Criar parcelas adicionais se necessário
        if installments > 1:
            for i in range(2, installments + 1):
                installment_date = transaction_date + relativedelta(months=i-1)
                
                installment_transaction = Transaction(
                    user_id=user_id,
                    category_id=category.id,
                    credit_card_id=credit_card_id,
                    description=f"{data['description']} - {i}/{installments}",
                    amount=installment_amount,
                    transaction_date=installment_date,
                    payment_type=data['payment_type'],
                    installments=installments,
                    installment_number=i,
                    parent_transaction_id=main_transaction.id
                )
                
                db.session.add(installment_transaction)
                created_transactions.append(installment_transaction)
        
        # Atualizar saldos
        if data['payment_type'] in ['debit', 'pix']:
            # Para débito/PIX, atualizar saldo da conta imediatamente
            if category.type == 'income':
                account.balance += amount
            else:  # expense
                account.balance -= amount
            account.updated_at = datetime.utcnow()
        
        elif data['payment_type'] == 'credit_card':
            # Para cartão de crédito, atualizar saldo do cartão
            if category.type == 'expense':
                credit_card.current_balance += amount
                credit_card.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': main_transaction.to_dict(),
            'installments_created': [t.to_dict(include_relations=False) for t in created_transactions],
            'message': 'Transação criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar transação: {str(e)}'}), 500

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transação não encontrada'}), 404
    
    try:
        # Se for uma transação parcelada (principal), excluir todas as parcelas
        if transaction.is_parent_transaction():
            child_transactions = Transaction.query.filter_by(parent_transaction_id=transaction.id).all()
            
            # Reverter saldos apenas da transação principal
            total_amount = transaction.amount * transaction.installments
            
            if transaction.payment_type in ['debit', 'pix'] and transaction.account:
                if transaction.category.type == 'income':
                    transaction.account.balance -= total_amount
                else:
                    transaction.account.balance += total_amount
                transaction.account.updated_at = datetime.utcnow()
            
            elif transaction.payment_type == 'credit_card' and transaction.credit_card:
                if transaction.category.type == 'expense':
                    transaction.credit_card.current_balance -= total_amount
                    transaction.credit_card.updated_at = datetime.utcnow()
            
            # Excluir parcelas filhas
            for child in child_transactions:
                db.session.delete(child)
        
        # Se for uma parcela individual, não permitir exclusão
        elif transaction.is_installment():
            return jsonify({'error': 'Não é possível excluir parcela individual. Exclua a transação principal.'}), 400
        
        # Se for transação única, reverter saldo
        else:
            if transaction.payment_type in ['debit', 'pix'] and transaction.account:
                if transaction.category.type == 'income':
                    transaction.account.balance -= transaction.amount
                else:
                    transaction.account.balance += transaction.amount
                transaction.account.updated_at = datetime.utcnow()
            
            elif transaction.payment_type == 'credit_card' and transaction.credit_card:
                if transaction.category.type == 'expense':
                    transaction.credit_card.current_balance -= transaction.amount
                    transaction.credit_card.updated_at = datetime.utcnow()
        
        # Excluir a transação principal
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transação excluída com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir transação: {str(e)}'}), 500

