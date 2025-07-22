from src.models.user import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' ou 'expense'
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

