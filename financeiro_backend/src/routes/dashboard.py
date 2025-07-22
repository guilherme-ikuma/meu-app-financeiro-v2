from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.account import Account
from src.models.credit_card import CreditCard
from src.models.transaction import Transaction
from src.models.category import Category
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__)

def require_auth():
    """Decorator para verificar autenticação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    return None

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    
    # Parâmetros de filtro de data (opcional)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Se não especificado, usar o mês atual
    if not start_date or not end_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    else:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
    
    # Saldo atual das contas
    accounts = Account.query.filter_by(user_id=user_id).all()
    current_balance = sum(float(acc.balance) for acc in accounts)
    
    # Cartões de crédito
    credit_cards = CreditCard.query.filter_by(user_id=user_id).all()
    credit_cards_data = []
    
    for card in credit_cards:
        credit_cards_data.append({
            'name': card.name,
            'current_balance': float(card.current_balance),
            'next_closing': card.get_next_closing_date().isoformat()
        })
    
    # Resumo mensal (baseado no filtro de data)
    income_query = db.session.query(func.sum(Transaction.amount)).join(Category).filter(
        and_(
            Transaction.user_id == user_id,
            Category.type == 'income',
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
    ).scalar() or 0
    
    expense_query = db.session.query(func.sum(Transaction.amount)).join(Category).filter(
        and_(
            Transaction.user_id == user_id,
            Category.type == 'expense',
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
    ).scalar() or 0
    
    total_income = float(income_query)
    total_expenses = float(expense_query)
    net_balance = total_income - total_expenses
    
    # Transações recentes (últimas 10)
    recent_transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())\
        .limit(10).all()
    
    recent_transactions_data = []
    for t in recent_transactions:
        recent_transactions_data.append({
            'id': t.id,
            'description': t.description,
            'amount': float(t.amount),
            'type': t.category.type,
            'date': t.transaction_date.isoformat(),
            'payment_type': t.payment_type,
            'installment_info': f"{t.installment_number}/{t.installments}" if t.installments > 1 else None
        })
    
    return jsonify({
        'current_balance': current_balance,
        'credit_cards': credit_cards_data,
        'monthly_summary': {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        },
        'recent_transactions': recent_transactions_data
    })

@dashboard_bp.route('/projections', methods=['GET'])
def get_projections():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    months = int(request.args.get('months', 12))
    
    # Saldo atual das contas
    accounts = Account.query.filter_by(user_id=user_id).all()
    current_balance = sum(float(acc.balance) for acc in accounts)
    
    projections = []
    today = date.today()
    
    for i in range(1, months + 1):
        projection_date = today + relativedelta(months=i)
        projection_year = projection_date.year
        projection_month = projection_date.month
        
        # Buscar parcelas que vencem neste mês
        month_start = date(projection_year, projection_month, 1)
        month_end = date(projection_year, projection_month, 1) + relativedelta(months=1, days=-1)
        
        # Parcelas de cartão de crédito que vencem neste mês
        installments = Transaction.query.join(Category).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.payment_type == 'credit_card',
                Category.type == 'expense',
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            )
        ).all()
        
        installments_data = []
        credit_card_expenses = 0
        
        for installment in installments:
            installments_data.append({
                'description': installment.description,
                'amount': float(installment.amount),
                'credit_card': installment.credit_card.name if installment.credit_card else None,
                'due_date': installment.get_installment_due_date().isoformat() if installment.get_installment_due_date() else None
            })
            credit_card_expenses += float(installment.amount)
        
        # Projeção simples: saldo atual menos gastos projetados
        projected_balance = current_balance - (credit_card_expenses * i)
        
        projections.append({
            'month': projection_month,
            'year': projection_year,
            'projected_balance': projected_balance,
            'credit_card_expenses': credit_card_expenses,
            'installments': installments_data
        })
    
    return jsonify({'projections': projections})

@dashboard_bp.route('/reports/summary', methods=['GET'])
def get_reports_summary():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    
    # Parâmetros
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    group_by = request.args.get('group_by', 'category')  # 'category' ou 'month'
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date e end_date são obrigatórios'}), 400
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de data inválido'}), 400
    
    if group_by == 'category':
        # Resumo por categoria
        income_by_category = db.session.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'income',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(Category.name).all()
        
        expense_by_category = db.session.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(Category.name).all()
        
        return jsonify({
            'income_by_category': [{'category': name, 'total': float(total)} for name, total in income_by_category],
            'expenses_by_category': [{'category': name, 'total': float(total)} for name, total in expense_by_category]
        })
    
    elif group_by == 'month':
        # Resumo por mês
        monthly_income = db.session.query(
            func.strftime('%Y-%m', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).join(Category).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'income',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(func.strftime('%Y-%m', Transaction.transaction_date)).all()
        
        monthly_expenses = db.session.query(
            func.strftime('%Y-%m', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).join(Category).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(func.strftime('%Y-%m', Transaction.transaction_date)).all()
        
        # Combinar dados por mês
        monthly_data = {}
        
        for month, total in monthly_income:
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expenses': 0}
            monthly_data[month]['income'] = float(total)
        
        for month, total in monthly_expenses:
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expenses': 0}
            monthly_data[month]['expenses'] = float(total)
        
        monthly_totals = []
        for month, data in sorted(monthly_data.items()):
            monthly_totals.append({
                'month': month,
                'income': data['income'],
                'expenses': data['expenses'],
                'net': data['income'] - data['expenses']
            })
        
        return jsonify({'monthly_totals': monthly_totals})
    
    else:
        return jsonify({'error': 'group_by deve ser "category" ou "month"'}), 400


@dashboard_bp.route('/dashboard/monthly-chart', methods=['GET'])
def get_monthly_chart():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_id = session['user_id']
    
    # Calcular dados dos últimos 6 meses
    today = date.today()
    chart_data = []
    
    for i in range(6):
        # Calcular o mês (i meses atrás)
        target_date = today - relativedelta(months=i)
        month_start = target_date.replace(day=1)
        month_end = date(target_date.year, target_date.month, 1) + relativedelta(months=1, days=-1)
        
        # Nome do mês em português
        month_names = [
            'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]
        month_name = f"{month_names[target_date.month - 1]}/{target_date.year}"
        
        # Buscar receitas do mês
        income_query = db.session.query(func.sum(Transaction.amount)).join(Category).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'income',
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            )
        ).scalar() or 0
        
        # Buscar despesas do mês
        expense_query = db.session.query(func.sum(Transaction.amount)).join(Category).filter(
            and_(
                Transaction.user_id == user_id,
                Category.type == 'expense',
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            )
        ).scalar() or 0
        
        receitas = float(income_query)
        despesas = float(expense_query)
        
        # Calcular projeção (baseada em transações parceladas futuras)
        projecao = 0
        if target_date >= today:  # Apenas para meses futuros
            # Buscar transações parceladas que afetam este mês
            parceladas = Transaction.query.join(Category).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.installments > 1,
                    Category.type == 'expense',
                    Transaction.transaction_date <= month_end
                )
            ).all()
            
            for t in parceladas:
                # Calcular quantas parcelas já foram pagas até este mês
                months_since = (target_date.year - t.transaction_date.year) * 12 + (target_date.month - t.transaction_date.month)
                if 0 <= months_since < t.installments:
                    projecao += float(t.amount) / t.installments
        
        chart_data.append({
            'month': month_name,
            'receitas': receitas,
            'despesas': despesas,
            'projecao': projecao
        })
    
    # Inverter para mostrar do mais antigo para o mais recente
    chart_data.reverse()
    
    return jsonify({
        'chart_data': chart_data
    })

