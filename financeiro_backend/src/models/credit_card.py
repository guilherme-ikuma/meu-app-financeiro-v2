from src.models.user import db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    closing_day = db.Column(db.Integer, nullable=False)  # Dia do fechamento (1-31)
    current_balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    transactions = db.relationship('Transaction', backref='credit_card', lazy=True)

    def __repr__(self):
        return f'<CreditCard {self.name}>'

    def get_next_closing_date(self):
        """Calcula a próxima data de fechamento da fatura"""
        today = date.today()
        
        # Data de fechamento do mês atual
        try:
            current_closing = date(today.year, today.month, self.closing_day)
        except ValueError:
            # Se o dia não existe no mês atual (ex: 31 em fevereiro), usa o último dia do mês
            current_closing = date(today.year, today.month, 1) + relativedelta(months=1, days=-1)
        
        # Se já passou do fechamento deste mês, próximo fechamento é no mês seguinte
        if today > current_closing:
            try:
                next_closing = date(today.year, today.month, self.closing_day) + relativedelta(months=1)
            except ValueError:
                next_closing = date(today.year, today.month, 1) + relativedelta(months=2, days=-1)
        else:
            next_closing = current_closing
            
        return next_closing

    def get_billing_month_for_date(self, transaction_date):
        """Determina em qual mês da fatura uma transação será incluída"""
        if isinstance(transaction_date, str):
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        elif isinstance(transaction_date, datetime):
            transaction_date = transaction_date.date()
        
        # Data de fechamento do mês da transação
        try:
            month_closing = date(transaction_date.year, transaction_date.month, self.closing_day)
        except ValueError:
            month_closing = date(transaction_date.year, transaction_date.month, 1) + relativedelta(months=1, days=-1)
        
        # Se a transação foi antes do fechamento, vai para a fatura do mês atual
        # Se foi depois, vai para a fatura do mês seguinte
        if transaction_date <= month_closing:
            return transaction_date.year, transaction_date.month
        else:
            next_month = transaction_date + relativedelta(months=1)
            return next_month.year, next_month.month

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'closing_day': self.closing_day,
            'current_balance': float(self.current_balance) if self.current_balance else 0.0,
            'next_closing': self.get_next_closing_date().isoformat(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

