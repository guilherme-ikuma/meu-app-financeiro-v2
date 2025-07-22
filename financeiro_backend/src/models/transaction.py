from src.models.user import db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)  # Para débito/PIX
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=True)  # Para cartão
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # 'debit', 'pix', 'credit_card'
    installments = db.Column(db.Integer, default=1)
    installment_number = db.Column(db.Integer, default=1)
    parent_transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    parent_transaction = db.relationship('Transaction', remote_side=[id], backref='child_transactions')
    account = db.relationship('Account', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.description}: {self.amount}>'

    def is_installment(self):
        """Verifica se é uma parcela de uma transação parcelada"""
        return self.parent_transaction_id is not None

    def is_parent_transaction(self):
        """Verifica se é a transação principal de um parcelamento"""
        return self.installments > 1 and self.installment_number == 1

    def get_installment_due_date(self):
        """Calcula a data de vencimento da parcela para cartão de crédito"""
        if self.payment_type != 'credit_card' or not self.credit_card:
            return None
        
        # Para a primeira parcela, usa a data da transação
        if self.installment_number == 1:
            base_date = self.transaction_date
        else:
            # Para parcelas subsequentes, adiciona meses
            base_date = self.transaction_date + relativedelta(months=self.installment_number - 1)
        
        # Determina o mês da fatura baseado na data e dia de fechamento
        billing_year, billing_month = self.credit_card.get_billing_month_for_date(base_date)
        
        # Data de fechamento da fatura
        try:
            closing_date = date(billing_year, billing_month, self.credit_card.closing_day)
        except ValueError:
            # Se o dia não existe no mês, usa o último dia
            closing_date = date(billing_year, billing_month, 1) + relativedelta(months=1, days=-1)
        
        return closing_date

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.0,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'payment_type': self.payment_type,
            'installments': self.installments,
            'installment_number': self.installment_number,
            'parent_transaction_id': self.parent_transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_relations:
            result.update({
                'category': self.category.to_dict() if self.category else None,
                'account': self.account.to_dict() if self.account else None,
                'credit_card': self.credit_card.to_dict() if self.credit_card else None,
                'due_date': self.get_installment_due_date().isoformat() if self.get_installment_due_date() else None
            })
        
        return result

